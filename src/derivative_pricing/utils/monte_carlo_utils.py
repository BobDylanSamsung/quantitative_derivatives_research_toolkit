from __future__ import annotations

import math
from time import perf_counter

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import linregress, norm

from derivative_pricing.models.market import MarketData
from derivative_pricing.models.options import EuropeanOption
from derivative_pricing.pricing.black_scholes_model import BlackScholesModel
from derivative_pricing.pricing.monte_carlo_model import MonteCarloModel


def run_variance_experiment(
    scenario: str,
    option: EuropeanOption,
    market: MarketData,
    simulation_counts: list[int],
    repetitions: int = 50,
    confidence_level: float = 0.95,
    base_seed: int = 42,
) -> pd.DataFrame:
    """Run repeated Monte Carlo experiments at different simulation counts.

    Each simulation count is tested using multiple independent random seeds.
    The Black-Scholes price is used as the analytical benchmark.

    Parameters
    ----------
    scenario
        Human-readable scenario name, such as ``"ATM"``.
    option
        European option being priced.
    market
        Market parameters.
    simulation_counts
        Numbers of Monte Carlo simulations to investigate.
    repetitions
        Number of independent runs at each simulation count.
    confidence_level
        Confidence level used by the Monte Carlo model.
    base_seed
        Starting seed used to construct reproducible independent runs.

    Returns
    -------
    pd.DataFrame
        One row per Monte Carlo run.
    """
    if repetitions < 2:
        raise ValueError("repetitions must be at least two")

    if any(count < 2 for count in simulation_counts):
        raise ValueError("all simulation counts must be at least two")

    black_scholes_price = float(
        BlackScholesModel(
            option=option,
            market=market,
        ).price
    )

    rows: list[dict[str, float | int | str | bool]] = []

    total_runs = repetitions * len(simulation_counts)

    for count_index, simulations in enumerate(simulation_counts):
        for repetition_index in range(repetitions):
            run_number = count_index * repetitions + repetition_index + 1

            seed = base_seed + count_index * repetitions + repetition_index

            print(
                f"[{run_number:,}/{total_runs:,}] "
                f"Running repetition {repetition_index + 1}/{repetitions} "
                f"with {simulations:,} simulations "
                f"(seed={seed})"
            )

            model = MonteCarloModel(
                option=option,
                market=market,
                simulations=simulations,
                seed=seed,
            )

            start = perf_counter()

            result = model.simulate(confidence_level=confidence_level)

            runtime_ms = (perf_counter() - start) * 1_000

            lower, upper = result.confidence_interval

            absolute_error = abs(result.price - black_scholes_price)

            relative_error = (
                absolute_error / black_scholes_price
                if black_scholes_price != 0.0
                else math.nan
            )

            rows.append(
                {
                    "scenario": scenario,
                    "simulations": simulations,
                    "repetition": repetition_index,
                    "seed": seed,
                    "black_scholes_price": (black_scholes_price),
                    "monte_carlo_price": result.price,
                    "standard_error": (result.standard_error),
                    "estimated_variance": (result.standard_error**2),
                    "ci_lower": lower,
                    "ci_upper": upper,
                    "ci_half_width": (upper - lower) / 2.0,
                    "absolute_error": absolute_error,
                    "relative_error": relative_error,
                    "squared_error": (result.price - black_scholes_price) ** 2,
                    "contains_black_scholes": (lower <= black_scholes_price <= upper),
                    "runtime_ms": runtime_ms,
                }
            )

    return pd.DataFrame(rows)


def summarise_variance_experiment(
    results: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate repeated Monte Carlo runs by simulation count."""

    summary = results.groupby(
        ["scenario", "simulations"],
        as_index=False,
    ).agg(
        black_scholes_price=(
            "black_scholes_price",
            "first",
        ),
        mean_monte_carlo_price=(
            "monte_carlo_price",
            "mean",
        ),
        empirical_variance=(
            "monte_carlo_price",
            "var",
        ),
        empirical_standard_deviation=(
            "monte_carlo_price",
            "std",
        ),
        mean_estimated_variance=(
            "estimated_variance",
            "mean",
        ),
        mean_standard_error=(
            "standard_error",
            "mean",
        ),
        mean_ci_half_width=(
            "ci_half_width",
            "mean",
        ),
        mean_absolute_error=(
            "absolute_error",
            "mean",
        ),
        mean_relative_error=(
            "relative_error",
            "mean",
        ),
        mean_squared_error=(
            "squared_error",
            "mean",
        ),
        confidence_interval_coverage=(
            "contains_black_scholes",
            "mean",
        ),
        mean_runtime_ms=(
            "runtime_ms",
            "mean",
        ),
    )

    summary["bias"] = summary["mean_monte_carlo_price"] - summary["black_scholes_price"]

    summary["rmse"] = np.sqrt(summary["mean_squared_error"])

    summary["variance_times_simulations"] = (
        summary["empirical_variance"] * summary["simulations"]
    )

    summary["se_times_sqrt_simulations"] = summary["mean_standard_error"] * np.sqrt(
        summary["simulations"]
    )

    return summary


def estimate_convergence_rates(
    summary: pd.DataFrame,
) -> pd.DataFrame:
    """Estimate log-log convergence slopes."""

    metrics = {
        "empirical_variance": -1.0,
        "mean_standard_error": -0.5,
        "rmse": -0.5,
        "mean_ci_half_width": -0.5,
    }

    rows: list[dict[str, float | str]] = []

    for scenario, scenario_df in summary.groupby("scenario"):
        scenario_name = str(scenario)

        scenario_df = scenario_df.sort_values("simulations")

        log_simulations = np.log(scenario_df["simulations"].to_numpy(dtype=float))

        for metric, theoretical_slope in metrics.items():
            values = scenario_df[metric].to_numpy(dtype=float)

            valid = np.isfinite(values) & (values > 0.0)

            regression = linregress(
                log_simulations[valid],
                np.log(values[valid]),
            )

            rows.append(
                {
                    "scenario": scenario_name,
                    "metric": metric,
                    "estimated_slope": float(regression.slope),
                    "theoretical_slope": theoretical_slope,
                    "r_squared": float(regression.rvalue**2),
                }
            )

    return pd.DataFrame(rows)


def estimate_required_simulations(
    option: EuropeanOption,
    market: MarketData,
    target_half_width: float,
    confidence_level: float = 0.95,
    pilot_simulations: int = 10_000,
    seed: int = 42,
) -> dict[str, float | int]:
    """Estimate simulations needed for a target CI half-width."""

    if target_half_width <= 0.0:
        raise ValueError("target_half_width must be positive")

    pilot_model = MonteCarloModel(
        option=option,
        market=market,
        simulations=pilot_simulations,
        seed=seed,
    )

    pilot_result = pilot_model.simulate(confidence_level=confidence_level)

    # Recover the sample standard deviation of the discounted
    # payoffs from SE = sample_sd / sqrt(N).
    estimated_payoff_sd = pilot_result.standard_error * math.sqrt(pilot_simulations)

    critical_value = float(norm.ppf(0.5 + confidence_level / 2.0))

    required_simulations = math.ceil(
        (critical_value * estimated_payoff_sd / target_half_width) ** 2
    )

    return {
        "pilot_simulations": pilot_simulations,
        "pilot_price": pilot_result.price,
        "estimated_discounted_payoff_sd": (estimated_payoff_sd),
        "confidence_level": confidence_level,
        "target_half_width": target_half_width,
        "required_simulations": max(
            required_simulations,
            2,
        ),
    }


def find_observed_required_simulations(
    summary: pd.DataFrame,
    target_half_width: float,
    minimum_coverage: float = 0.90,
) -> pd.DataFrame:
    """Find the first tested count satisfying the precision target."""

    rows: list[dict[str, float | int | str | None]] = []

    for scenario, scenario_df in summary.groupby("scenario"):
        scenario_df = scenario_df.sort_values("simulations")

        eligible = scenario_df[
            (scenario_df["mean_ci_half_width"] <= target_half_width)
            & (scenario_df["confidence_interval_coverage"] >= minimum_coverage)
        ]

        if eligible.empty:
            rows.append(
                {
                    "scenario": str(scenario),
                    "target_half_width": (target_half_width),
                    "required_simulations": None,
                    "achieved_half_width": None,
                    "coverage": None,
                }
            )
            continue

        first = eligible.iloc[0]

        rows.append(
            {
                "scenario": str(scenario),
                "target_half_width": (target_half_width),
                "required_simulations": int(first["simulations"]),
                "achieved_half_width": float(first["mean_ci_half_width"]),
                "coverage": float(first["confidence_interval_coverage"]),
            }
        )

    return pd.DataFrame(rows)


def plot_price_convergence(
    results: pd.DataFrame,
    scenario: str,
    repetition: int = 0,
) -> None:
    data = results[
        (results["scenario"] == scenario) & (results["repetition"] == repetition)
    ].sort_values("simulations")

    prices = data["monte_carlo_price"].to_numpy()

    lower_errors = prices - data["ci_lower"].to_numpy()

    upper_errors = data["ci_upper"].to_numpy() - prices

    black_scholes_price = float(data["black_scholes_price"].iloc[0])

    _, ax = plt.subplots()

    ax.errorbar(
        data["simulations"],
        prices,
        yerr=np.vstack([lower_errors, upper_errors]),
        marker="o",
        capsize=3,
        label="Monte Carlo estimate and 95% CI",
    )

    ax.axhline(
        black_scholes_price,
        linestyle="--",
        label="Black–Scholes price",
    )

    ax.set_xscale("log")
    ax.set_xlabel("Number of simulations")
    ax.set_ylabel("Option price")
    ax.set_title(f"{scenario} Monte Carlo price convergence")
    ax.legend()
    ax.grid(True)

    plt.show()


def plot_variance_convergence(
    summary: pd.DataFrame,
    scenario: str,
) -> None:
    data = summary[summary["scenario"] == scenario].sort_values("simulations")

    simulations = data["simulations"].to_numpy(dtype=float)

    empirical_variance = data["empirical_variance"].to_numpy(dtype=float)

    reference_variance = empirical_variance[0] * simulations[0] / simulations

    _, ax = plt.subplots()

    ax.loglog(
        simulations,
        empirical_variance,
        marker="o",
        label="Empirical estimator variance",
    )

    ax.loglog(
        simulations,
        reference_variance,
        linestyle="--",
        label=r"Reference: $N^{-1}$",
    )

    ax.set_xlabel("Number of simulations")
    ax.set_ylabel("Variance of price estimate")
    ax.set_title(f"{scenario} Monte Carlo variance convergence")
    ax.legend()
    ax.grid(True)

    plt.show()


def plot_error_convergence(
    summary: pd.DataFrame,
    scenario: str,
) -> None:
    data = summary[summary["scenario"] == scenario].sort_values("simulations")

    simulations = data["simulations"].to_numpy(dtype=float)

    standard_error = data["mean_standard_error"].to_numpy(dtype=float)

    reference_error = standard_error[0] * np.sqrt(simulations[0] / simulations)

    _, ax = plt.subplots()

    ax.loglog(
        simulations,
        standard_error,
        marker="o",
        label="Mean estimated standard error",
    )

    ax.loglog(
        simulations,
        data["rmse"],
        marker="o",
        label="Empirical RMSE",
    )

    ax.loglog(
        simulations,
        reference_error,
        linestyle="--",
        label=r"Reference: $N^{-1/2}$",
    )

    ax.set_xlabel("Number of simulations")
    ax.set_ylabel("Pricing error")
    ax.set_title(f"{scenario} Monte Carlo error convergence")
    ax.legend()
    ax.grid(True)

    plt.show()


def plot_confidence_interval_coverage(
    summary: pd.DataFrame,
    scenario: str,
    confidence_level: float = 0.95,
) -> None:
    data = summary[summary["scenario"] == scenario].sort_values("simulations")

    _, ax = plt.subplots()

    ax.plot(
        data["simulations"],
        data["confidence_interval_coverage"],
        marker="o",
        label="Empirical coverage",
    )

    ax.axhline(
        confidence_level,
        linestyle="--",
        label="Target coverage",
    )

    ax.set_xscale("log")
    ax.set_ylim(0.0, 1.05)
    ax.set_xlabel("Number of simulations")
    ax.set_ylabel("Coverage rate")
    ax.set_title(f"{scenario} confidence-interval coverage")
    ax.legend()
    ax.grid(True)

    plt.show()
