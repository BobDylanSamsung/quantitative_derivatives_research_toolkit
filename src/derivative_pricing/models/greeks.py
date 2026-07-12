from dataclasses import dataclass


@dataclass
class Greeks:
    delta: float
    gamma: float
    vega: float
    theta: float
    rho: float
