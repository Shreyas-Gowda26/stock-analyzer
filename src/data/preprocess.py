import pandas as pd
from pathlib import Path


def load_raw_data():
    """
    Load the raw stock market dataset.
    """

    file_path = Path("data/raw/indian_stocks.csv")

    df = pd.read_csv(file_path, header=[0, 1], index_col=0)

    return df


if __name__ == "__main__":

    df = load_raw_data()

    print("First 5 rows:")
    print(df.head())

    print("\nShape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns)