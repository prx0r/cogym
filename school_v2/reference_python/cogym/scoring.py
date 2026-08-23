from __future__ import annotations
import math
from .schema import Decision

ACTION_SIGN={"LONG":1.0,"FLAT":0.0,"SHORT":-1.0}

def score_decision(d: Decision, realized_return: float) -> tuple[float,float,float]:
    """Returns reward, regret, calibration error.

    Reward mixes directional paper-PnL and forecast accuracy; no real execution occurs.
    """
    sign=ACTION_SIGN[d.action]
    pnl=sign*realized_return
    oracle=abs(realized_return)
    regret=max(0.0, oracle-pnl)
    forecast_err=abs(d.expected_return-realized_return)
    reward=pnl - 0.25*forecast_err
    event=1.0 if ((d.expected_return>=0) == (realized_return>=0)) else 0.0
    calibration=abs(d.confidence-event)
    return reward,regret,calibration
