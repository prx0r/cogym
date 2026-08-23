"""RichMarketPacket: everything the LLM sees at each decision point.
Includes market data + portfolio state + evidence options."""
from __future__ import annotations
from dataclasses import dataclass, field

@dataclass(frozen=True)
class RichMarketPacket:
    """Everything the LLM sees. No hidden state."""
    step: int
    total_steps: int
    
    # Market data
    price: float
    price_change_pct: float          # vs previous bar
    direction_5bar: float            # 5-bar momentum
    direction_20bar: float           # 20-bar momentum  
    volatility_20bar: float
    volume_ratio: float              # current vol / avg vol
    drawdown_from_peak: float        # how far below recent high
    trend_label: str                 # "uptrend" | "downtrend" | "sideways"
    
    # Portfolio state (from PaperTradingEngine)
    cash: float
    position: float                  # +long -short 0 flat
    unrealized_pnl: float
    total_pnl: float
    win_rate: str                    # "65%" format for readability
    n_trades: int
    max_drawdown_so_far: str
    
    # Evidence marketplace
    available_evidence: list[dict]   # [{"name":"orderbook_depth","cost":2,"description":"..."}]
    
    # Recent history the agent can see
    recent_decisions: list[dict]     # last 3 decisions with outcomes
    
    def to_prompt(self) -> str:
        """Formats everything into a clear prompt section for the LLM."""
        lines = []
        lines.append(f"--- MARKET STATE (step {self.step}/{self.total_steps}) ---")
        lines.append(f"Price: ${self.price:.2f} ({self.price_change_pct:+.2%} this bar)")
        lines.append(f"Trend: {self.trend_label} | 5-bar momentum: {self.direction_5bar:+.4f}")
        lines.append(f"20-bar momentum: {self.direction_20bar:+.4f} | Volatility: {self.volatility_20bar:.4f}")
        lines.append(f"Volume ratio: {self.volume_ratio:.1f}x | Drawdown from peak: {self.drawdown_from_peak:.1%}")
        
        lines.append(f"\n--- YOUR PORTFOLIO ---")
        lines.append(f"Cash: ${self.cash:.2f} | Position: {self.position:+.4f}")
        if self.position != 0:
            lines.append(f"Unrealized PnL: ${self.unrealized_pnl:.2f}")
        lines.append(f"Total PnL: ${self.total_pnl:.2f}")
        lines.append(f"Trades: {self.n_trades} | Win rate: {self.win_rate} | Max DD: {self.max_drawdown_so_far}")
        
        if self.recent_decisions:
            lines.append(f"\n--- RECENT DECISIONS ---")
            for d in self.recent_decisions[-3:]:
                lines.append(f"  Step {d.get('step','?')}: {d.get('action','?')} "
                           f"(PnL: {d.get('pnl','?')}) → {d.get('outcome','?')}")
        
        if self.available_evidence:
            lines.append(f"\n--- EVIDENCE AVAILABLE (costs tokens) ---")
            for ev in self.available_evidence:
                lines.append(f"  {ev['name']}: {ev['description']} [cost: {ev['cost']} credits]")
        
        return "\n".join(lines)
