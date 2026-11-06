
import json
from src.agents.technical_agent import run_technical_agent

REPORT_PATH = "data/processed/technical_reports.json"


def main():
    with open(REPORT_PATH, "r") as file:
        reports = json.load(file)

    print(f"\nTesting Technical Analysis Agent")
    print(f"Total stocks: {len(reports)}")

    for stock in reports:
        ticker = stock["ticker"]

        print("\n" + "=" * 70)
        print(f"ANALYSING: {ticker}")
        print("=" * 70)

        result = run_technical_agent(json.dumps(stock, indent=4))

        print("\n========== AI TECHNICAL ANALYSIS ==========\n")
        print(result)

        print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
