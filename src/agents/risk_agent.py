
from crewai import Agent, Task, Crew, Process

from src.agents.llm_config import llm


def create_risk_agent():

    agent = Agent(
        role="Stock Market Risk Analyst",

        goal=(
            "Interpret supplied stock risk metrics and explain "
            "the assigned risk classifications using only the "
            "provided numerical evidence."
        ),

        backstory=(
            "You are an experienced stock market risk analyst "
            "specializing in annualized volatility and drawdown "
            "analysis. You explain risk classifications clearly, "
            "distinguish current risk from historical risk and "
            "never invent metrics or make unsupported predictions."
        ),

        llm=llm,
        verbose=False,
        allow_delegation=False,
        max_iter=3
    )

    return agent


def create_risk_task(agent):

    task = Task(
        description="""
        Analyze the following stock risk report.

        STOCK RISK DATA:
        {risk_report}

        Your analysis must contain these four sections:

        1. STOCK OVERVIEW
           - Identify the stock ticker.
           - State the report date.
           - State the supplied overall risk classification.

        2. VOLATILITY ANALYSIS
           - Explain the supplied annualized volatility.
           - State its supplied risk classification.
           - Explain what the metric represents without
             inventing additional interpretations.

        3. DRAWDOWN ANALYSIS
           - Explain current drawdown and its supplied
             risk classification.
           - Explain maximum historical drawdown and its
             supplied risk classification.
           - Clearly distinguish current drawdown from
             historical maximum drawdown.

        4. OVERALL RISK ASSESSMENT
           - State the supplied overall risk classification.
           - Explain the contribution of the supplied risk
             categories to the overall assessment.
           - Identify the main risk factors using the
             supplied report only.

        STRICT DATA RULES:

        - Use only the supplied risk report.
        - Never invent numerical values.
        - Do not calculate additional financial statistics.
        - Do not derive new numerical values.
        - Do not estimate missing information.
        - Preserve all supplied classifications exactly.
        - Do not change Low Risk, Moderate Risk or High Risk
          classifications.
        - If information is unavailable, explicitly state so.

        VOLATILITY RULES:

        - Explain annualized volatility using its supplied value.
        - Do not independently classify volatility.
        - Do not compare it with other stocks unless comparative
          data is explicitly supplied.
        - Do not predict future price fluctuations.

        DRAWDOWN RULES:

        - Current drawdown represents the decline from the
          running historical peak in the available dataset.
        - Maximum historical drawdown represents the largest
          observed peak-to-trough decline in that dataset.
        - Do not calculate recovery percentages.
        - Do not interpret historical drawdown as a prediction
          of future losses.
        - Do not describe current drawdown as maximum drawdown.

        OVERALL RISK RULES:

        - The deterministic Risk Engine has already assigned
          the overall risk classification.
        - Your responsibility is to explain that classification,
          not recalculate or replace it.
        - Use the supplied volatility and drawdown classifications
          to explain the overall assessment.
        - Do not invent additional risk factors.
        - Do not provide buy or sell recommendations.

        OUTPUT RULES:

        - Complete all four requested sections.
        - Keep the report concise and understandable.
        - Every numerical claim must match the input.
        - Avoid repeating the same information unnecessarily.
        - Clearly distinguish historical risk from future risk.
        - Do not make stock price predictions.
        - Do not guarantee future returns.
        - End every section and sentence properly.
        """,

        expected_output="""
        A structured stock risk analysis containing all four
        requested sections:

        1. Stock Overview
        2. Volatility Analysis
        3. Drawdown Analysis
        4. Overall Risk Assessment

        All numerical values and risk classifications must
        match the supplied risk report exactly. No additional
        calculations, unsupported comparisons or predictions.
        """,

        agent=agent
    )

    return task


def run_risk_agent(risk_report):

    agent = create_risk_agent()
    task = create_risk_task(agent)

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=False
    )

    result = crew.kickoff(
        inputs={
            "risk_report": risk_report
        }
    )

    return result
