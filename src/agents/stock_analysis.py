
import json
from pathlib import Path

from src.agents.technical_agent import run_technical_agent
from src.agents.risk_agent import run_risk_agent


TECHNICAL_REPORT_PATH = Path(
    "data/processed/technical_reports.json"
)

RISK_REPORT_PATH = Path(
    "data/processed/risk_reports.json"
)

OUTPUT_DIR = Path(
    "data/processed/final_reports"
)


def load_reports():

    with TECHNICAL_REPORT_PATH.open("r") as file:
        technical_reports = json.load(file)

    with RISK_REPORT_PATH.open("r") as file:
        risk_reports = json.load(file)

    return technical_reports, risk_reports


def validate_reports(technical_reports, risk_reports):

    technical_tickers = {
        report["ticker"] for report in technical_reports
    }

    risk_tickers = {
        report["ticker"] for report in risk_reports
    }

    if technical_tickers != risk_tickers:
        raise ValueError(
            "Technical and risk reports contain different stocks."
        )


def run_stock_analysis(ticker, selected_agents):

    # Validate agent selection
    valid_agents = {"technical", "risk"}

    if not selected_agents:
        raise ValueError("Select at least one AI analyst.")

    if not set(selected_agents).issubset(valid_agents):
        raise ValueError("Invalid AI analyst selection.")

    # Load existing calculated reports
    technical_reports, risk_reports = load_reports()

    validate_reports(technical_reports, risk_reports)

    # Find reports for the requested stock only
    technical_report = next(
        (
            report for report in technical_reports
            if report["ticker"] == ticker
        ),
        None
    )

    risk_report = next(
        (
            report for report in risk_reports
            if report["ticker"] == ticker
        ),
        None
    )

    if technical_report is None or risk_report is None:
        raise ValueError(
            f"Technical or risk data unavailable for {ticker}."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = OUTPUT_DIR / (
        f"{ticker.replace('.', '_')}.json"
    )

    # Preserve an existing report if one is already available
    if output_file.exists():
        with output_file.open("r") as file:
            final_report = json.load(file)
    else:
        final_report = {
            "ticker": ticker,
            "date": technical_report["date"],
            "overall_risk": risk_report["overall_risk"]
        }

    # Keep report metadata current
    final_report["ticker"] = ticker
    final_report["date"] = technical_report["date"]
    final_report["overall_risk"] = risk_report["overall_risk"]

    generated_agents = set(
        final_report.get("generated_agents", [])
    )

    # Run only the selected agents
    if "technical" in selected_agents:

        print(f"Running Technical Analyst for {ticker}...")

        technical_result = run_technical_agent(
            json.dumps(technical_report, indent=4)
        )

        final_report["technical_analysis"] = str(
            technical_result
        )

        generated_agents.add("technical")

    if "risk" in selected_agents:

        print(f"Running Risk Analyst for {ticker}...")

        risk_result = run_risk_agent(
            json.dumps(risk_report, indent=4)
        )

        final_report["risk_analysis"] = str(
            risk_result
        )

        generated_agents.add("risk")

    final_report["generated_agents"] = sorted(
        generated_agents
    )

    # Save the updated report
    with output_file.open("w") as file:
        json.dump(final_report, file, indent=4)

    print(f"Analysis completed for {ticker}.")
    print(f"Saved: {output_file}")

    return final_report
