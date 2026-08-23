"""Paper-trading backtest engine for Cogym.
Tracks portfolio state, computes rolling metrics, supports evidence purchases.
The LLM sees ALL of this at each decision point — giving it quantitative feedback
to reason over instead of guessing blind.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import math

@dataclass
class PortfolioState:
    """Everything the agent should know about its current position."""
    step: int = 0
    total_steps: int = 0
    cash: float = 10_000.0
    position: float = 0.0          # +long, -short, 0 flat
    entry_price: float = 0.0
    current_price: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    total_pnl: float = 0.0
    equity_curve: list[float] = field(default_factory=list)
    
    # rolling stats
    n_trades: int = 0
    wins: int = 0
    losses: int = 0
    win_rate: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    profit_factor: float = 0.0
    
    # risk metrics
    peak_equity: float = 10_000.0
    max_drawdown_pct: float = 0.0
    current_drawdown_pct: float = 0.0
    sharpe_so_far: float = 0.0
    
    def summary_for_llm(self) -> dict:
        """What the LLM sees. All numeric, no hidden state."""
        return {
            "step": f"{self.step}/{self.total_steps}",
            "cash": round(self.cash, 2),
            "position": round(self.position, 4),
            "entry_price": round(self.entry_price, 2),
            "current_price": round(self.current_price, 2),
            "unrealized_pnl": round(self.unrealized_pnl, 2),
            "realized_pnl": round(self.realized_pnl, 2),
            "total_pnl": round(self.total_pnl, 2),
            "total_return_pct": round((self.total_pnl / 10000) * 100, 2),
            "n_trades": self.n_trades,
            "win_rate": f"{self.win_rate:.0%}",
            "avg_win": round(self.avg_win, 2),
            "avg_loss": round(self.avg_loss, 2),
            "profit_factor": round(self.profit_factor, 2) if self.profit_factor else "N/A",
            "max_drawdown": f"{self.max_drawdown_pct:.1%}",
            "current_drawdown": f"{self.current_drawdown_pct:.1%}",
        }


@dataclass
class TradingMetrics:
    """Post-hoc analysis. Computed once at episode end."""
    total_return: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    max_drawdown: float = 0.0
    calmar_ratio: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    n_trades: int = 0
    avg_trade_duration: int = 0
    best_trade: float = 0.0
    worst_trade: float = 0.0
    evidence_cost_total: float = 0.0
    
    def to_dict(self) -> dict:
        return {k: round(v, 6) if isinstance(v, float) else v for k, v in self.__dict__.items()}


class PaperTradingEngine:
    """Deterministic paper-trading simulation.
    Same world + same actions = same outcome. Always."""
    
    def __init__(self, initial_capital: float = 10_000.0,
                 commission_bps: float = 5.0):
        self.initial_capital = initial_capital
        self.commission_rate = commission_bps / 10_000
        
    def execute(self, prices: list[float], actions: list[dict]) -> tuple[PortfolioState, TradingMetrics]:
        """Run through all bars executing agent decisions.
        
        Each action is {"action": "LONG"|"SHORT"|"FLAT", "size": float, "confidence": float}
        """
        st = PortfolioState(
            total_steps=len(prices),
            cash=self.initial_capital,
            current_price=prices[0],
        )
        st.equity_curve.append(st.cash)
        
        returns = []
        trade_pnls = []
        
        for i, price in enumerate(prices):
            st.step = i + 1
            st.current_price = price
            
            action = actions[i] if i < len(actions) else {"action": "FLAT"}
            
            # Close existing position if direction changes or FLAT
            old_pos = st.position
            new_target = 0.0
            act = action.get("action", "FLAT")
            
            if act == "LONG":
                new_target = min(1.0, action.get("size", 1.0))
            elif act == "SHORT":
                new_target = -min(1.0, action.get("size", 1.0))
            
            # Execute position change
            if abs(new_target - old_pos) > 0.01:
                # Close old position
                if old_pos != 0:
                    pnl = old_pos * (price - st.entry_price)
                    commission = abs(old_pos) * price * self.commission_rate * 2
                    st.realized_pnl += pnl - commission
                    st.n_trades += 1
                    
                    if pnl > 0:
                        st.wins += 1
                    elif pnl < 0:
                        st.losses += 1
                    
                    trade_pnls.append(pnl - commission)
                
                # Open new position
                if new_target != 0:
                    st.entry_price = price
                    commission = abs(new_target) * price * self.commission_rate
                    st.realized_pnl -= commission
                
                st.position = new_target
            
            # Update unrealized PnL
            if st.position != 0 and st.entry_price > 0:
                st.unrealized_pnl = st.position * (price - st.entry_price)
            else:
                st.unrealized_pnl = 0.0
            
            st.total_pnl = st.realized_pnl + st.unrealized_pnl
            
            equity = self.initial_capital + st.total_pnl
            st.equity_curve.append(equity)
            
            # Rolling stats
            if st.wins + st.losses > 0:
                st.win_rate = st.wins / (st.wins + st.losses)
            
            if trade_pnls:
                wins_pnls = [p for p in trade_pnls if p > 0]
                losses_pnls = [p for p in trade_pnls if p <= 0]
                st.avg_win = sum(wins_pnls) / len(wins_pnls) if wins_pnls else 0
                st.avg_loss = abs(sum(losses_pnls) / len(losses_pnls)) if losses_pnls else 0
                gross_loss = sum(losses_pnls) if losses_pnls else 0
                gross_profit = sum(wins_pnls) if wins_pnls else 0
                st.profit_factor = abs(gross_profit / gross_loss) if gross_loss else float('inf') if gross_profit else 0
            
            # Drawdown tracking
            peak = max(st.equity_curve)
            st.current_drawdown_pct = (peak - equity) / peak if peak > 0 else 0
            st.max_drawdown_pct = max(st.max_drawdown_pct, st.current_drawdown_pct)
            
            # Track returns for Sharpe
            if len(st.equity_curve) > 1:
                r = (st.equity_curve[-1] - st.equity_curve[-2]) / st.equity_curve[-2] if st.equity_curve[-2] > 0 else 0
                returns.append(r)
        
        # Compute final metrics
        m = TradingMetrics()
        m.total_return = st.total_pnl / self.initial_capital
        m.n_trades = st.n_trades
        m.win_rate = st.win_rate
        
        if returns and len(returns) > 1:
            mean_r = sum(returns) / len(returns)
            std_r = math.sqrt(sum((r - mean_r)**2 for r in returns) / (len(returns)-1)) if len(returns)>1 else 1
            m.sharpe_ratio = mean_r / std_r * math.sqrt(252) if std_r > 0 else 0
            
            neg_returns = [r for r in returns if r < 0]
            if neg_returns:
                std_neg = math.sqrt(sum(r**2 for r in neg_returns) / len(neg_returns))
                m.sortino_ratio = mean_r / std_neg * math.sqrt(252) if std_neg > 0 else 0
        
        m.max_drawdown = st.max_drawdown_pct
        m.calmar_ratio = m.total_return / m.max_drawdown if m.max_drawdown > 0 else 0
        
        if trade_pnls:
            m.best_trade = max(trade_pnls)
            m.worst_trade = min(trade_pnls)
        
        return st, m


def compute_metrics_summary(prices: list[float], actions: list[dict],
                            initial_capital: float = 10000) -> dict:
    """Convenience function. Returns everything the LLM needs to reason about its performance."""
    engine = PaperTradingEngine(initial_capital=initial_capital)
    final_state, metrics = engine.execute(prices, actions)
    return {
        "final_state": final_state.summary_for_llm(),
        "metrics": metrics.to_dict(),
    }
