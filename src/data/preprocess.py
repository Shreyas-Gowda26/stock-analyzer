import pandas as pd
from pathlib import Path


RAW_FILE = Path("data/raw/indian_stocks.csv")
PROCESSED_FILE = Path("data/processed/indian_stocks_clean.csv")
MONTHLY_FILE = Path("data/processed/indian_stocks_monthly.csv")


def load_raw_data():
    """Load the raw yfinance dataset."""

    df = pd.read_csv(
        RAW_FILE,
        header=[0, 1],
        index_col=0
    )

    return df


def standardize_data(df):
    """Convert raw MultiIndex data into a clean tabular structure."""

    # Convert index to datetime
    df.index = pd.to_datetime(df.index)

    # Sort chronologically
    df = df.sort_index()

    # Convert MultiIndex into long/tidy format
    df = df.stack(level="Ticker").reset_index()

    # Rename columns
    df.columns = [
        "Date",
        "Ticker",
        "Close",
        "High",
        "Low",
        "Open",
        "Volume"
    ]

    # Arrange columns in conventional OHLCV order
    df = df[
        [
            "Date",
            "Ticker",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume"
        ]
    ]

    # Sort by stock and date
    df = df.sort_values(
        ["Ticker", "Date"]
    ).reset_index(drop=True)

    return df


def validate_data(df):
    """Perform data-quality checks."""

    print("\n========== DATA VALIDATION ==========")

    # Missing values
    print("\nMissing values:")
    print(df.isnull().sum())

    # Duplicate records
    duplicates = df.duplicated().sum()

    print(f"\nDuplicate records: {duplicates}")

    # Duplicate ticker-date combinations
    duplicate_dates = df.duplicated(
        subset=["Ticker", "Date"]
    ).sum()

    print(
        f"Duplicate ticker-date records: "
        f"{duplicate_dates}"
    )

    # Numeric columns
    numeric_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]

    print("\nData types:")
    print(df[numeric_columns].dtypes)

    # Invalid prices
    invalid_prices = (
        (df["Open"] <= 0)
        | (df["High"] <= 0)
        | (df["Low"] <= 0)
        | (df["Close"] <= 0)
    ).sum()

    print(f"\nInvalid price records: {invalid_prices}")

    # Invalid volume
    invalid_volume = (
        df["Volume"] < 0
    ).sum()

    print(f"Invalid volume records: {invalid_volume}")

    # OHLC consistency
    invalid_ohlc = (
        (df["High"] < df["Open"])
        | (df["High"] < df["Close"])
        | (df["High"] < df["Low"])
        | (df["Low"] > df["Open"])
        | (df["Low"] > df["Close"])
        | (df["Low"] > df["High"])
    ).sum()

    print(f"Invalid OHLC records: {invalid_ohlc}")


def clean_data(df):
    """Clean missing, duplicate and invalid records."""

    # Remove duplicate ticker-date records
    df = df.drop_duplicates(
        subset=["Ticker", "Date"],
        keep="first"
    )

    # Remove rows with missing essential market values
    required_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]

    df = df.dropna(
        subset=required_columns
    )

    # Remove invalid price records
    df = df[
        (df["Open"] > 0)
        & (df["High"] > 0)
        & (df["Low"] > 0)
        & (df["Close"] > 0)
    ]

    # Volume cannot be negative
    df = df[df["Volume"] >= 0]

    # OHLC logical validation
    df = df[
        (df["High"] >= df["Open"])
        & (df["High"] >= df["Close"])
        & (df["High"] >= df["Low"])
        & (df["Low"] <= df["Open"])
        & (df["Low"] <= df["Close"])
        & (df["Low"] <= df["High"])
    ]

    return df.reset_index(drop=True)


def align_dates(df):
    """
    Keep only dates available for all selected stocks.
    """

    stock_count = df["Ticker"].nunique()

    date_counts = (
        df.groupby("Date")["Ticker"]
        .nunique()
    )

    common_dates = date_counts[
        date_counts == stock_count
    ].index

    df = df[
        df["Date"].isin(common_dates)
    ]

    return df.reset_index(drop=True)


def create_features(df):
    """Create return and moving-average features."""

    df = df.sort_values(
        ["Ticker", "Date"]
    ).reset_index(drop=True)

    # Absolute daily price change
    df["Price_Change"] = (
        df.groupby("Ticker")["Close"]
        .diff()
    )

    # Daily percentage return
    df["Daily_Return"] = (
        df.groupby("Ticker")["Close"]
        .pct_change()
    )

    # 50-day moving average
    df["MA50"] = (
        df.groupby("Ticker")["Close"]
        .transform(
            lambda x: x.rolling(50).mean()
        )
    )

    # 200-day moving average
    df["MA200"] = (
        df.groupby("Ticker")["Close"]
        .transform(
            lambda x: x.rolling(200).mean()
        )
    )

    return df


def create_monthly_summary(df):
    """Create monthly return and price summary."""

    monthly = (
        df.set_index("Date")
        .groupby("Ticker")
        .resample("ME")
        .agg(
            Closing_Price=("Close", "last"),
        )
        .reset_index()
    )

    # Calculate actual monthly return
    monthly["Monthly_Return"] = (
        monthly
        .groupby("Ticker")["Closing_Price"]
        .pct_change()
    )

    return monthly


def final_validation(df):
    """Perform final checks before exporting."""

    print("\n========== FINAL VALIDATION ==========")

    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print(f"Stocks: {df['Ticker'].nunique()}")

    print(
        f"Date range: "
        f"{df['Date'].min().date()} "
        f"to "
        f"{df['Date'].max().date()}"
    )

    # Validate core OHLCV data separately
    core_columns = [
        "Date",
        "Ticker",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]

    print("\nMissing values in core market data:")
    print(df[core_columns].isnull().sum())

    print(
        "\nTotal missing values in core market data:",
        df[core_columns].isnull().sum().sum()
    )

    # Check derived features separately
    feature_columns = [
        "Price_Change",
        "Daily_Return",
        "MA50",
        "MA200"
    ]

    print("\nMissing values in derived features:")
    print(df[feature_columns].isnull().sum())

    # Duplicate checks
    print(
        "\nDuplicate records:",
        df.duplicated().sum()
    )

    print(
        "Duplicate ticker-date records:",
        df.duplicated(
            subset=["Ticker", "Date"]
        ).sum()
    )

    # Date ordering
    is_sorted = (
        df.sort_values(["Ticker", "Date"])
        .reset_index(drop=True)
        .equals(df.reset_index(drop=True))
    )

    print(
        "Chronologically sorted:",
        is_sorted
    )

    print("\nStocks:")
    print(df["Ticker"].unique())

    print("\nFinal columns:")
    print(df.columns.tolist())

def save_data(df, monthly):
    """Save processed datasets."""

    # Create processed directory if it doesn't exist
    PROCESSED_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save cleaned daily data
    df.to_csv(
        PROCESSED_FILE,
        index=False
    )

    # Save monthly summary
    monthly.to_csv(
        MONTHLY_FILE,
        index=False
    )

    print(
        f"\nProcessed data saved to: "
        f"{PROCESSED_FILE}"
    )

    print(
        f"Monthly summary saved to: "
        f"{MONTHLY_FILE}"
    )

if __name__ == "__main__":

    print("Loading raw data...")

    df = load_raw_data()

    print(f"Raw shape: {df.shape}")

    # Standardization
    df = standardize_data(df)

    print(
        f"\nShape after standardization: "
        f"{df.shape}"
    )

    # Validation before cleaning
    validate_data(df)

    # Cleaning
    df = clean_data(df)

    print(
        f"\nShape after cleaning: "
        f"{df.shape}"
    )

    # Align stocks to common dates
    df = align_dates(df)

    print(
        f"Shape after date alignment: "
        f"{df.shape}"
    )

    # Feature creation
    df = create_features(df)

    # Monthly summary
    monthly = create_monthly_summary(df)

    # Final validation
    final_validation(df)

    # Save
    save_data(df, monthly)