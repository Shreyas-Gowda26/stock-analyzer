
import json
from pathlib import Path


REPORT_PATH = Path("data/processed/technical_reports.json")


def classify_volatility(volatility):
    if volatility < 20:
        return "Low Risk"
    elif volatility < 35:
        return "Moderate Risk"
    else:
        return "High Risk"


def classify_drawdown(drawdown):
    drawdown = abs(drawdown)

    if drawdown < 10:
        return "Low Risk"
    elif drawdown < 25:
        return "Moderate Risk"
    else:
        return "High Risk"


def generate_risk_report(stock_reports):
    risk_reports = []

    for stock in stock_reports:
        volatility = stock["volatility"]["annualized_volatility"]
        
        current_drawdown = stock["risk"]["current_drawdown"]
        max_drawdown = stock["risk"]["maximum_historical_drawdown"]

        risk_report = {
            "ticker": stock["ticker"],
            "date": stock["date"],
            "volatility": {
                "annualized_volatility": volatility,
                "risk_level": classify_volatility(volatility)
            },
            "drawdown": {
                "current_drawdown": current_drawdown,
                "current_risk_level": classify_drawdown(current_drawdown),
                "maximum_historical_drawdown": max_drawdown,
                "historical_risk_level": classify_drawdown(max_drawdown)
            }
        }
        risk_report["overall_risk"] = calculate_overall_risk(
        risk_report["volatility"]["risk_level"],
        risk_report["drawdown"]["current_risk_level"],
        risk_report["drawdown"]["historical_risk_level"]
        )
        risk_reports.append(risk_report)

    return risk_reports


def calculate_overall_risk(volatility_risk, current_risk, historical_risk):
    risk_levels = [
        volatility_risk,
        current_risk,
        historical_risk
    ]

    high_count = risk_levels.count("High Risk")
    moderate_count = risk_levels.count("Moderate Risk")

    if high_count >= 2:
        return "High Risk"
    elif high_count + moderate_count >= 2:
        return "Moderate Risk"
    else:
        return "Low Risk"

def main():
    with REPORT_PATH.open("r") as file:
        stock_reports = json.load(file)

    risk_reports = generate_risk_report(stock_reports)
    output_path = Path("data/processed/risk_reports.json")

    with output_path.open("w") as file:
        json.dump(risk_reports, file, indent=4)

    print(f"\nRisk reports saved to: {output_path}")
    for report in risk_reports:
        print(report)


if __name__ == "__main__":
    main()
