from __future__ import annotations

import json
from datetime import UTC, date, datetime
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

from derivative_pricing.calibration.implied_volatility import ImpliedVolatilitySolver
from derivative_pricing.models.market import CalibrationMarketData
from derivative_pricing.models.options import EuropeanOption, OptionType


def select_target_expirations(
    expirations: list[str],
    as_of: datetime,
    target_days: tuple[int, ...] = (30, 90, 180),
    minimum_days: int = 14,
    maximum_days: int = 365,
) -> list[str]:
    """Select the available expirations closest to target maturities."""

    available = [
        (
            expiration,
            (date.fromisoformat(expiration) - as_of.date()).days,
        )
        for expiration in expirations
    ]

    eligible = [
        (expiration, days_to_expiry)
        for expiration, days_to_expiry in available
        if minimum_days <= days_to_expiry <= maximum_days
    ]

    if not eligible:
        raise RuntimeError("No expirations found inside the requested maturity range")

    selected: list[str] = []

    for target in target_days:
        expiration, _ = min(
            eligible,
            key=lambda candidate: abs(candidate[1] - target),
        )

        if expiration not in selected:
            selected.append(expiration)

    return sorted(selected)


def download_option_chain(
    symbol: str,
    target_days: tuple[int, ...] = (30, 90, 180),
) -> tuple[pd.DataFrame, dict[str, object]]:
    ticker = yf.Ticker(symbol)

    expirations = list(ticker.options)

    if not expirations:
        raise RuntimeError(f"No option expirations returned for {symbol}")

    history = ticker.history(period="5d")

    if history.empty:
        raise RuntimeError(f"No spot-price history returned for {symbol}")

    spot = float(history["Close"].dropna().iloc[-1])
    fetched_at = datetime.now(UTC)

    selected_expirations = select_target_expirations(
        expirations=expirations,
        as_of=fetched_at,
        target_days=target_days,
    )

    frames: list[pd.DataFrame] = []

    for expiration in selected_expirations:
        chain = ticker.option_chain(expiration)

        for option_type, frame in (
            ("call", chain.calls),
            ("put", chain.puts),
        ):
            if frame.empty:
                continue

            prepared = frame.copy()
            prepared["symbol"] = symbol
            prepared["option_type"] = option_type
            prepared["expiration"] = expiration
            prepared["spot"] = spot
            prepared["fetched_at_utc"] = fetched_at.isoformat()

            frames.append(prepared)

    if not frames:
        raise RuntimeError(f"No option contracts returned for {symbol}")

    quotes = pd.concat(frames, ignore_index=True)

    metadata: dict[str, object] = {
        "symbol": symbol,
        "spot": spot,
        "fetched_at_utc": fetched_at.isoformat(),
        "expirations": selected_expirations,
        "target_days": list(target_days),
        "source": "Yahoo Finance via yfinance",
    }

    return quotes, metadata


def save_snapshot(
    quotes: pd.DataFrame,
    metadata: dict[str, object],
    output_directory: Path,
) -> None:
    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")

    symbol = str(metadata["symbol"])

    quotes.to_csv(
        output_directory / f"{symbol}_{timestamp}.csv",
        index=False,
    )

    with (output_directory / f"{symbol}_{timestamp}_metadata.json").open("w") as file:
        json.dump(
            metadata,
            file,
            indent=2,
        )


def prepare_option_chain(
    quotes: pd.DataFrame,
) -> pd.DataFrame:
    df = quotes.copy()

    df["expiration"] = pd.to_datetime(
        df["expiration"],
    )

    df["fetched_at_utc"] = pd.to_datetime(
        df["fetched_at_utc"],
        utc=True,
    )

    quote_date = df["fetched_at_utc"].dt.tz_convert(None).dt.normalize()

    expiration_date = df["expiration"].dt.normalize()

    df["days_to_expiry"] = (expiration_date - quote_date).dt.days

    df["maturity"] = df["days_to_expiry"] / 365.0

    df["mid_price"] = (df["bid"] + df["ask"]) / 2.0

    df["spread"] = df["ask"] - df["bid"]

    df["relative_spread"] = np.where(
        df["mid_price"] > 0,
        df["spread"] / df["mid_price"],
        np.nan,
    )

    df["spot_moneyness"] = df["strike"] / df["spot"]

    return df


def filter_option_chain(
    quotes: pd.DataFrame,
    minimum_days_to_expiry: int = 14,
    maximum_days_to_expiry: int = 365,
    minimum_moneyness: float = 0.80,
    maximum_moneyness: float = 1.20,
    maximum_relative_spread: float = 0.30,
    minimum_open_interest: int = 10,
) -> pd.DataFrame:
    return quotes[
        (quotes["bid"] > 0)
        & (quotes["ask"] > quotes["bid"])
        & (quotes["mid_price"] > 0)
        & (quotes["days_to_expiry"] >= minimum_days_to_expiry)
        & (quotes["days_to_expiry"] <= maximum_days_to_expiry)
        & (quotes["spot_moneyness"] >= minimum_moneyness)
        & (quotes["spot_moneyness"] <= maximum_moneyness)
        & (quotes["relative_spread"] <= maximum_relative_spread)
        & (quotes["openInterest"].fillna(0) >= minimum_open_interest)
    ].copy()


def calibrate_option_quote(
    row: pd.Series,
    dividend_yield: float,
    risk_free_rate: float,
) -> pd.Series:
    """Calculate implied volatility for one option quote."""

    option_type = {
        "call": OptionType.CALL,
        "put": OptionType.PUT,
    }[str(row["option_type"]).lower()]

    option = EuropeanOption(
        strike=float(row["strike"]),
        maturity=float(row["maturity"]),
        type=option_type,
    )

    market = CalibrationMarketData(
        spot=float(row["spot"]),
        risk_free_rate=risk_free_rate,
        dividend_yield=dividend_yield,
    )

    result = ImpliedVolatilitySolver(
        option=option,
        market=market,
        market_price=float(row["mid_price"]),
    ).solve()

    return pd.Series(
        {
            "risk_free_rate": risk_free_rate,
            "dividend_yield": dividend_yield,
            "model_implied_volatility": result.volatility,
            "iv_converged": result.converged,
            "iv_iterations": result.iterations,
            "iv_failure_reason": result.reason,
        }
    )


def calibrate_option_chain(
    quotes: pd.DataFrame,
    dividend_yield: float,
    risk_free_rate: float,
) -> pd.DataFrame:
    calibration_results = quotes.apply(
        calibrate_option_quote,
        axis=1,
        dividend_yield=dividend_yield,
        risk_free_rate=risk_free_rate,
    )

    return pd.concat(
        [
            quotes.reset_index(drop=True),
            calibration_results.reset_index(drop=True),
        ],
        axis=1,
    )
