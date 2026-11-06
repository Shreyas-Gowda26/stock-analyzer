
import json
from pathlib import Path

from src.agents.technical_agent import run_technical_agent
from src.agents.risk_agent import run_risk_agent


BASE_DIR = Path(__file__).resolve().parents[2]

TECHNICAL_FILE = (
    BASE_DIR / "data/processed/technical_reports.json"
)

RISK_FILE = (
    BASE_DIR / "data/processed/risk_reports.json"
)


with TECHNICAL_FILE.open("r") as file:
    technical_reports = json.load(file)

with RISK_FILE.open("r") as file:
    risk_reports = json.load(file)


ticker = "HDFCBANK.NS"

technical_report = next(
    report for report in technical_reports
    if report["ticker"] == ticker
)

risk_report = next(
    report for report in risk_reports
    if report["ticker"] == ticker
)


print(f"\nTesting agents for {ticker}\n")

print("Running Technical Agent...")

technical_result = run_technical_agent(
    json.dumps(technical_report, indent=4)
)

print("\nTECHNICAL ANALYSIS")
print(technical_result)

print("\nRunning Risk Agent...")

risk_result = run_risk_agent(
    json.dumps(risk_report, indent=4)
)

print("\nRISK ANALYSIS")
print(risk_result)

print("\nBoth agents completed successfully.")
