
import pandas as pd
import numpy as np


DATA_PATH = "data/processed/indian_stocks_clean.csv"


def load_data():
    """Load and prepare cleaned stock data."""
    df = pd.read_csv(DATA_PATH)

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values(["Ticker", "Date"]).reset_index(drop=True)

    return df


def calculate_rsi(group, period=14):
    """Calculate RSI using Wilder's exponential smoothing."""
    delta = group["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1 / period,
        min_periods=period,
        adjust=False
    ).mean()

    avg_loss = loss.ewm(
        alpha=1 / period,
        min_periods=period,
        adjust=False
    ).mean()

    rs = avg_gain / avg_loss

    group["RSI"] = 100 - (100 / (1 + rs))

    return group


def calculate_macd(group):
    """Calculate MACD, signal line and histogram."""
    ema_12 = group["Close"].ewm(
        span=12, adjust=False
    ).mean()

    ema_26 = group["Close"].ewm(
        span=26, adjust=False
    ).mean()

    group["MACD"] = ema_12 - ema_26

    group["MACD_Signal"] = group["MACD"].ewm(
        span=9, adjust=False
    ).mean()

    group["MACD_Histogram"] = (
        group["MACD"] - group["MACD_Signal"]
    )

    return group


def calculate_bollinger_bands(group, period=20):
    """Calculate Bollinger Bands."""
    middle = group["Close"].rolling(period).mean()

    std = group["Close"].rolling(period).std(ddof=0)

    group["BB_Middle"] = middle
    group["BB_Upper"] = middle + (2 * std)
    group["BB_Lower"] = middle - (2 * std)

    return group


def calculate_atr(group, period=14):
    """Calculate Average True Range."""
    previous_close = group["Close"].shift(1)

    high_low = group["High"] - group["Low"]
    high_previous = (group["High"] - previous_close).abs()
    low_previous = (group["Low"] - previous_close).abs()

    true_range = pd.concat(
        [high_low, high_previous, low_previous],
        axis=1
    ).max(axis=1)

    group["ATR"] = true_range.ewm(
        alpha=1 / period,
        min_periods=period,
        adjust=False
    ).mean()

    return group


def calculate_volatility(group, period=20):
    """Calculate annualized rolling volatility as a percentage."""
    daily_returns = group["Close"].pct_change()

    group["Volatility"] = (
        daily_returns.rolling(period).std(ddof=1)
        * np.sqrt(252)
        * 100
    )

    return group


def calculate_drawdown(group):
    """Calculate running drawdown from historical peak."""
    running_peak = group["Close"].cummax()

    group["Drawdown"] = (
        (group["Close"] / running_peak) - 1
    ) * 100

    return group


def calculate_technical_indicators(df):
    """Calculate all technical indicators independently per stock."""

    results = []

    for ticker, group in df.groupby("Ticker", sort=False):

        group = group.copy()
        group = group.sort_values("Date")

        group = calculate_rsi(group)
        group = calculate_macd(group)
        group = calculate_bollinger_bands(group)
        group = calculate_atr(group)
        group = calculate_volatility(group)
        group = calculate_drawdown(group)

        results.append(group)

    return pd.concat(results, ignore_index=True)


def run_analysis():
    df = load_data()

    df = calculate_technical_indicators(df)

    return df


if __name__ == "__main__":
    result = run_analysis()

    print("\nTechnical Analysis Completed!")
    print("Total records:", len(result))

    print("\nLatest indicators for each stock:")

    latest = (
        result.sort_values("Date")
        .groupby("Ticker")
        .tail(1)
    )

    columns = [
        "Ticker",
        "Date",
        "Close",
        "RSI",
        "MACD",
        "MACD_Signal",
        "BB_Upper",
        "BB_Lower",
        "ATR",
        "Volatility",
        "Drawdown"
    ]

    print(latest[columns].to_string(index=False))
