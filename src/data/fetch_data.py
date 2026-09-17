import yfinance as yf
from pathlib import Path


STOCKS = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
]


def fetch_stock_data(tickers, period="1y", interval="1d"):
    """
    Download historical stock data from Yahoo Finance.
    """

    df = yf.download(
        tickers=tickers,
        period=period,
        interval=interval,
        auto_adjust=True,
        group_by="column",
        progress=True
    )

    return df


def save_raw_data(df):
    """
    Save the raw downloaded dataset.
    """

    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "indian_stocks.csv"

    df.to_csv(output_path)

    print(f"Raw data saved to: {output_path}")


if __name__ == "__main__":

    df = fetch_stock_data(STOCKS)

    print("\nFirst 5 rows:")
    print(df.head())

    print("\nShape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns)

    save_raw_data(df)