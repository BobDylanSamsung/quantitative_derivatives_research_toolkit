from dataclasses import dataclass


@dataclass(frozen=True)
class ImpliedVolatilityResult:
    volatility: float | None
    converged: bool
    iterations: int | None
    reason: str | None = None
