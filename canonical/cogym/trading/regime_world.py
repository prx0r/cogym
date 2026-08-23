"""Interactive regime-shift world. 30 sequential decisions.
Hidden regime change at trial 16. Agent must detect and adapt.
Primary metric: post_shift_cumulative_regret."""
from __future__ import annotations
import math, random
from dataclasses import dataclass, field

from .engine import PaperTradingEngine, PortfolioState, TradingMetrics

@dataclass(frozen=True)
class RegimeWorldSpec:
    seed: int = 42
    total_steps: int = 30
    shift_point: int = 16          # hidden change point
    regime_a_drift: float = 0.002  # positive drift (bullish)
    regime_a_vol: float = 0.01
    regime_b_drift: float = -0.003 # negative drift (bearish)  
    regime_b_vol: float = 0.02
    evidence_cost_base: float = 1.0
    
class InteractiveRegimeWorld:
    """Sequential trading world with hidden regime shift.
    The agent doesn't know when or if the regime changes.
    It must detect the change from price behavior."""
    
    def __init__(self, spec: RegimeWorldSpec):
        self.spec = spec
        self.rng = random.Random(spec.seed)
        # Pre-generate all returns deterministically
        self.prices = []
        self.regimes = []   # for oracle only
        price = 100.0
        
        for step in range(spec.total_steps):
            if step < spec.shift_point:
                drift, vol = spec.regime_a_drift, spec.regime_a_vol
            else:
                drift, vol = spec.regime_b_drift, spec.regime_b_vol
            
            ret = self.rng.gauss(drift, vol)
            price *= (1 + ret)
            self.prices.append(price)
            self.regimes.append("A" if step < spec.shift_point else "B")
        
        self.engine = PaperTradingEngine()
        self.portfolio: PortfolioState | None = None
        self.evidence_purchased: list[str] = []
        self.evidence_costs: dict[str, float] = {
            "volatility_forecast": spec.evidence_cost_base * 2,
            "momentum_analysis": spec.evidence_cost_base,
            "support_resistance": spec.evidence_cost_base * 1.5,
            "correlation_check": spec.evidence_cost_base * 3,
        }
        self.recent_decisions: list[dict] = []
    
    def reset(self):
        self.engine = PaperTradingEngine()
        self.evidence_purchased = []
        self.recent_decisions = []
    
    @property
    def current_regime(self) -> str:
        return self.regimes[min(len(self.regimes)-1, max(0,self._step))]
    
    def get_observation(self, step: int) -> dict:
        """What the agent sees at this point. NO future data."""
        price = self.prices[step]
        lookback = min(10, step)
        past_prices = self.prices[max(0,step-lookback):step+1]
        
        returns = [(past_prices[i+1]-past_prices[i])/past_prices[i] 
                   for i in range(len(past_prices)-1)]
        
        mean_ret = sum(returns)/len(returns) if returns else 0
        std_ret = math.sqrt(sum((r-mean_ret)**2 for r in returns)/len(returns)) if len(returns)>1 else 0.01
        
        peak = max(past_prices)
        dd = (peak - price) / peak if peak > 0 else 0
        
        # Simple trend label
        if len(returns) >= 5:
            recent_mean = sum(returns[-5:]) / 5
        else:
            recent_mean = mean_ret
        
        trend = "uptrend" if recent_mean > 0.001 else "downtrend" if recent_mean < -0.001 else "sideways"
        
        portfolio_summary = self.portfolio.summary_for_llm() if self.portfolio else {}
        
        evidence_options = [
            {"name": name, "cost": f"{cost:.0f} credits",
             "description": desc} 
            for name, cost, desc in [
                ("volatility_forecast", self.spec.evidence_cost_base*2,
                 "Predicted volatility range for next 5 bars"),
                ("momentum_analysis", self.spec.evidence_cost_base,
                 "Detailed momentum breakdown across timeframes"),
                ("support_resistance", self.spec.evidence_cost_base*1.5,
                 "Key support/resistance levels from order book simulation"),
                ("correlation_check", self.spec.evidence_cost_base*3,
                 "Cross-asset correlation matrix — may reveal regime shifts"),
            ]
        ]
        
        return {
            "step": step + 1,
            "total_steps": self.spec.total_steps,
            "price": round(price, 2),
            "recent_returns": [round(r,5) for r in returns[-5:]],
            "trend_label": trend,
            "estimated_volatility": round(std_ret, 4),
            "drawdown_from_peak": round(dd, 4),
            "portfolio": portfolio_summary,
            "evidence_available": evidence_options,
        }
    
    def score_action(self, action: str, step: int) -> float:
        """Deterministic scoring. LONG profits if price goes up next bar."""
        if step >= len(self.prices) - 1:
            return 0.0
        ret = (self.prices[step+1] - self.prices[step]) / self.prices[step]
        if action == "CHOOSE_A":    # long
            return ret
        elif action == "CHOOSE_B":  # short
            return -ret
        return 0.0
    
    def compute_post_shift_regret(self, actions: list[str]) -> float:
        """Cumulative regret after the regime shift. The primary metric."""
        total_oracle = 0.0
        total_agent = 0.0
        for step in range(self.spec.shift_point, min(len(actions), len(self.prices)-1)):
            ret = (self.prices[step+1] - self.prices[step]) / self.prices[step]
            oracle_action = "CHOOSE_A" if ret > 0 else "CHOOSE_B"
            agent_reward = self.score_action(actions[step], step)
            oracle_reward = abs(ret)  # perfect prediction gets full move
            total_agent += agent_reward
            total_oracle += oracle_reward
        
        return total_oracle - total_agent  # lower = better
