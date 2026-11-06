
import json
from pathlib import Path

from src.agents.risk_agent import run_risk_agent


REPORT_PATH = Path("data/processed/risk_reports.json")


def main():
    with REPORT_PATH.open("r") as file:
        reports = json.load(file)

    # Test with the first stock only
    stock = reports[0]

    print("\nTesting Risk Analysis Agent")
    print("Stock:", stock["ticker"])

    result = run_risk_agent(json.dumps(stock, indent=4))

    print("\n========== AI RISK ANALYSIS ==========\n")
    print(result)


if __name__ == "__main__":
    main()
