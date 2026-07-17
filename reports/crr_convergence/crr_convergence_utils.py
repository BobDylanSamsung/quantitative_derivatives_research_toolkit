import math

import ipywidgets as widgets
import matplotlib.pyplot as plt
import pandas as pd
from IPython.display import clear_output

from derivative_pricing.models.market import MarketData
from derivative_pricing.models.options import EuropeanOption, OptionType
from derivative_pricing.pricing.black_scholes_model import BlackScholesModel
from derivative_pricing.pricing.cox_ross_rubenstein_model import CoxRossRubinsteinModel


def plot_price_convergence(
    df: pd.DataFrame,
    ax: plt.Axes,
) -> None:
    black_scholes_price = df["black_scholes_price"].iloc[0]

    ax.plot(
        df["steps"],
        df["crr_price"],
        label="CRR price",
    )
    ax.axhline(
        black_scholes_price,
        linestyle="--",
        label="Black-Scholes",
    )

    ax.set_xlabel("Number of CRR steps")
    ax.set_ylabel("Option price")
    ax.set_title("Price convergence")
    ax.legend()
    ax.grid()


def plot_absolute_error(
    df: pd.DataFrame,
    ax: plt.Axes,
) -> None:
    ax.plot(
        df["steps"],
        df["absolute_error"],
    )

    ax.set_xlabel("Number of CRR steps")
    ax.set_ylabel("Absolute pricing error")
    ax.set_title("Absolute error")
    ax.grid()


def plot_log_log_error(
    df: pd.DataFrame,
    ax: plt.Axes,
) -> None:
    filtered = df[(df["steps"] > 0) & (df["absolute_error"] > 0)]

    ax.loglog(
        filtered["steps"],
        filtered["absolute_error"],
        marker="o",
        markersize=2,
    )

    ax.set_xlabel("Number of CRR steps")
    ax.set_ylabel("Absolute pricing error")
    ax.set_title("Log-log convergence")
    ax.grid()


def plot_odd_even_convergence(
    df: pd.DataFrame,
    ax: plt.Axes,
) -> None:
    even_df = df[df["steps"] % 2 == 0]
    odd_df = df[df["steps"] % 2 == 1]

    black_scholes_price = df["black_scholes_price"].iloc[0]

    ax.plot(
        even_df["steps"],
        even_df["crr_price"],
        label="Even steps",
    )
    ax.plot(
        odd_df["steps"],
        odd_df["crr_price"],
        label="Odd steps",
    )
    ax.axhline(
        black_scholes_price,
        linestyle="--",
        label="Black-Scholes",
    )

    ax.set_xlabel("Number of CRR steps")
    ax.set_ylabel("Option price")
    ax.set_title("Odd-even convergence")
    ax.legend()
    ax.grid()


def plot_scenario(
    df: pd.DataFrame,
    scenario_name: str,
    description: str,
) -> None:
    fig, axes = plt.subplots(
        nrows=2,
        ncols=2,
        figsize=(16, 12),
    )

    plot_price_convergence(df, axes[0, 0])
    plot_absolute_error(df, axes[0, 1])
    plot_log_log_error(df, axes[1, 0])
    plot_odd_even_convergence(df, axes[1, 1])

    fig.suptitle(
        f"{scenario_name} call option: {description}",
        fontsize=16,
    )
    fig.tight_layout()
    plt.show()


def plot_moneyness_comparison(
    results: dict[str, pd.DataFrame],
) -> None:
    fig, axes = plt.subplots(
        nrows=1,
        ncols=3,
        figsize=(20, 6),
    )

    for scenario_name, df in results.items():
        axes[0].plot(
            df["steps"],
            df["crr_price"],
            label=scenario_name,
        )

        axes[1].plot(
            df["steps"],
            df["absolute_error"],
            label=scenario_name,
        )

        relative_error_df = df[df["relative_error"] > 0]

        axes[2].loglog(
            relative_error_df["steps"],
            relative_error_df["relative_error"],
            label=scenario_name,
        )

    axes[0].set_title("CRR prices")
    axes[0].set_xlabel("Number of CRR steps")
    axes[0].set_ylabel("Option price")
    axes[0].legend()
    axes[0].grid()

    axes[1].set_title("Absolute pricing error")
    axes[1].set_xlabel("Number of CRR steps")
    axes[1].set_ylabel("Absolute error")
    axes[1].legend()
    axes[1].grid()

    axes[2].set_title("Relative pricing error")
    axes[2].set_xlabel("Number of CRR steps")
    axes[2].set_ylabel("Relative error")
    axes[2].legend()
    axes[2].grid()

    fig.tight_layout()
    plt.show()


def investigate_crr_convergence(
    option: EuropeanOption,
    market: MarketData,
    step_counts: list[int],
) -> pd.DataFrame:
    black_scholes_price = BlackScholesModel(
        option=option,
        market=market,
    ).price

    rows = []

    for steps in step_counts:
        crr_price = CoxRossRubinsteinModel(
            option=option,
            market=market,
            steps=steps,
        ).price()

        signed_error = crr_price - black_scholes_price
        absolute_error = abs(signed_error)

        rows.append(
            {
                "steps": steps,
                "crr_price": crr_price,
                "black_scholes_price": black_scholes_price,
                "signed_error": signed_error,
                "absolute_error": absolute_error,
                "relative_error": (
                    absolute_error / abs(black_scholes_price)
                    if black_scholes_price != 0
                    else math.nan
                ),
            }
        )

    return pd.DataFrame(rows)


def create_convergence_ui() -> widgets.VBox:
    option_type_input = widgets.ToggleButtons(
        options=[
            ("Call", OptionType.CALL),
            ("Put", OptionType.PUT),
        ],
        value=OptionType.CALL,
        description="Option:",
    )

    strike_input = widgets.FloatSlider(
        value=100.0,
        min=10.0,
        max=250.0,
        step=1.0,
        description="Strike:",
        continuous_update=False,
    )

    maturity_input = widgets.FloatSlider(
        value=1.0,
        min=0.05,
        max=5.0,
        step=0.05,
        description="Maturity:",
        continuous_update=False,
    )

    spot_input = widgets.FloatSlider(
        value=100.0,
        min=10.0,
        max=250.0,
        step=1.0,
        description="Spot:",
        continuous_update=False,
    )

    risk_free_rate_input = widgets.FloatSlider(
        value=0.05,
        min=-0.05,
        max=0.20,
        step=0.005,
        description="Rate:",
        readout_format=".3f",
        continuous_update=False,
    )

    volatility_input = widgets.FloatSlider(
        value=0.20,
        min=0.01,
        max=1.00,
        step=0.01,
        description="Volatility:",
        continuous_update=False,
    )

    minimum_steps_input = widgets.IntSlider(
        value=1,
        min=1,
        max=100,
        step=1,
        description="Min steps:",
        continuous_update=False,
    )

    maximum_steps_input = widgets.IntSlider(
        value=500,
        min=10,
        max=5_000,
        step=10,
        description="Max steps:",
        continuous_update=False,
    )

    step_increment_input = widgets.IntSlider(
        value=1,
        min=1,
        max=100,
        step=1,
        description="Increment:",
        continuous_update=False,
    )

    run_button = widgets.Button(
        description="Run investigation",
        button_style="primary",
        icon="play",
    )

    output = widgets.Output()

    def handle_run(_: widgets.Button) -> None:
        with output:
            clear_output(wait=True)

            if minimum_steps_input.value > maximum_steps_input.value:
                print("Minimum steps must not exceed maximum steps.")
                return

            option = EuropeanOption(
                strike=strike_input.value,
                maturity=maturity_input.value,
                type=option_type_input.value,
            )

            market = MarketData(
                spot=spot_input.value,
                risk_free_rate=risk_free_rate_input.value,
                volatility=volatility_input.value,
            )

            step_counts = list(
                range(
                    minimum_steps_input.value,
                    maximum_steps_input.value + 1,
                    step_increment_input.value,
                )
            )

            try:
                df = investigate_crr_convergence(option, market, step_counts)
                plot_scenario(df, "", "")
            except Exception as exc:
                print(f"Error: {exc}")

    run_button.on_click(handle_run)

    controls = widgets.HBox(
        [
            widgets.VBox(
                [
                    widgets.HTML("<h3>Option</h3>"),
                    option_type_input,
                    strike_input,
                    maturity_input,
                ]
            ),
            widgets.VBox(
                [
                    widgets.HTML("<h3>Market</h3>"),
                    spot_input,
                    risk_free_rate_input,
                    volatility_input,
                ]
            ),
            widgets.VBox(
                [
                    widgets.HTML("<h3>Convergence</h3>"),
                    minimum_steps_input,
                    maximum_steps_input,
                    step_increment_input,
                    run_button,
                ]
            ),
        ]
    )

    return widgets.VBox([controls, output])
