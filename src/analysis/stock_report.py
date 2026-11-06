
from src.analysis.technical_analysis import run_analysis
import pandas as pd
import json

def get_rsi_signal(rsi):
    if pd.isna(rsi):
        return "Insufficient data"

    if rsi >= 70:
        return "Overbought"
    elif rsi >= 50:
        return "Positive momentum"
    elif rsi > 30:
        return "Negative momentum"
    else:
        return "Oversold"


def get_macd_signal(macd, signal):
    if macd > signal:
        return "Bullish momentum"
    elif macd < signal:
        return "Bearish momentum"
    return "Neutral momentum"


def get_trend_signal(close, ma50, ma200):
    if close > ma50 and ma50 > ma200:
        return "Strong upward trend"
    elif close < ma50 and ma50 < ma200:
        return "Strong downward trend"
    return "Mixed trend"


def generate_stock_report(df):
    reports = []

    for ticker, group in df.groupby("Ticker"):

        group = group.sort_values("Date")
        latest = group.iloc[-1]

        report = {
            "ticker": ticker,
            "date": str(latest["Date"].date()),

            "price": {
                "close": round(float(latest["Close"]), 2),
                "daily_return": round(
                    float(latest["Daily_Return"]) * 100, 2
                )
            },

            "momentum": {
                "rsi": round(float(latest["RSI"]), 2),
                "rsi_signal": get_rsi_signal(latest["RSI"]),
                "macd": round(float(latest["MACD"]), 2),
                "macd_signal": round(float(latest["MACD_Signal"]), 2),
                "macd_histogram": round(
                    float(latest["MACD_Histogram"]), 2
                ),
                "macd_interpretation": get_macd_signal(
                    latest["MACD"],
                    latest["MACD_Signal"]
                )
            },

            "volatility": {
                "atr": round(float(latest["ATR"]), 2),
                "annualized_volatility": round(
                    float(latest["Volatility"]), 2
                ),
                "bollinger_upper": round(
                    float(latest["BB_Upper"]), 2
                ),
                "bollinger_lower": round(
                    float(latest["BB_Lower"]), 2
                )
            },

            "risk": {
                "current_drawdown": round(
                    float(latest["Drawdown"]), 2
                ),
                "maximum_historical_drawdown": round(
                    float(group["Drawdown"].min()), 2
                )
            },
            "trend": {
                "ma50": round(float(latest["MA50"]), 2),
                "ma200": round(float(latest["MA200"]), 2),
                "interpretation": get_trend_signal(
                    latest["Close"],
                    latest["MA50"],
                    latest["MA200"]
                )
            }
        }

        reports.append(report)

    return reports


if __name__ == "__main__":

    df = run_analysis()
    reports = generate_stock_report(df)

    with open(
        "data/processed/technical_reports.json",
        "w"
    ) as file:
        json.dump(reports, file, indent=4)

    print("Technical reports generated successfully!")
    print("Stocks analysed:", len(reports))
    print("Saved to: data/processed/technical_reports.json")