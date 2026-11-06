
#!/bin/bash

set -euo pipefail

PROJECT_DIR="/Users/shreyasg/Projects/stock-market-ai"
PYTHON="$PROJECT_DIR/dashboard_venv/bin/python"

cd "$PROJECT_DIR"

mkdir -p logs

LOG_FILE="$PROJECT_DIR/logs/update_$(date +%Y-%m-%d).log"

# Redirect all output to the log file
exec >> "$LOG_FILE" 2>&1

echo "========================================"
echo "Indian Stock Market Data Update"
echo "Started: $(date)"
echo "========================================"

if [[ ! -x "$PYTHON" ]]; then
    echo "ERROR: Python interpreter not found: $PYTHON"
    exit 1
fi

echo ""
echo "Step 1: Fetching latest stock data..."
"$PYTHON" -m src.data.fetch_data

echo ""
echo "Step 2: Preprocessing stock data..."
"$PYTHON" -m src.data.preprocess

echo ""
echo "Step 3: Verifying generated files..."

for file in \
    data/raw/indian_stocks.csv \
    data/processed/indian_stocks_clean.csv \
    data/processed/indian_stocks_monthly.csv
do
    if [[ ! -s "$file" ]]; then
        echo "ERROR: Missing or empty file: $file"
        exit 1
    fi
    echo "Verified: $file"
done

echo ""
echo "Step 4: Checking latest trading date..."

"$PYTHON" -c '
import pandas as pd

df = pd.read_csv("data/processed/indian_stocks_clean.csv")
df["Date"] = pd.to_datetime(df["Date"])

print("Latest trading date:", df["Date"].max().date())
print("Total records:", len(df))
print("Stocks:", df["Ticker"].nunique())
'

echo ""
echo "========================================"
echo "DATA UPDATE COMPLETED SUCCESSFULLY"
echo "Finished: $(date)"
echo "========================================"
