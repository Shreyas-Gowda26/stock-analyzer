
from crewai import Agent, Task, Crew, Process

from src.agents.llm_config import llm


def create_technical_agent():

    agent = Agent(
        role="Senior Technical Market Analyst",

        goal=(
            "Interpret supplied technical indicators accurately "
            "and explain a stock's price momentum, trend, volatility "
            "and historical risk without making unsupported "
            "calculations, assumptions or predictions."
        ),

        backstory=(
            "You are an experienced technical market analyst "
            "specializing in RSI, MACD, moving averages, Bollinger "
            "Bands, ATR, volatility and drawdown. You carefully "
            "interpret numerical evidence, identify conflicting "
            "signals and distinguish observations from supplied "
            "interpretations. You never invent data or claim "
            "certainty about future market movements."
        ),

        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3
    )

    return agent


def create_technical_task(agent):

    task = Task(
        description="""
        Analyze the following technical stock report.

        STOCK DATA:
        {stock_report}

        Your analysis must contain these six sections:

        1. PRICE OVERVIEW
           - Explain the latest closing price.
           - Interpret the supplied daily return.
           - Describe the observed price movement without
             predicting future movement.

        2. MOMENTUM ANALYSIS
           - Interpret RSI using its supplied value and signal.
           - Explain the MACD value and signal line.
           - Interpret the MACD histogram.
           - Explain whether RSI and MACD agree or conflict.

        3. TREND ANALYSIS
           - Interpret MA50 and MA200.
           - Explain the supplied trend interpretation.
           - Distinguish the current price position relative
             to the moving averages when the values are supplied.
           - Explain conflicting short-term and broader trend signals.

        4. VOLATILITY ANALYSIS
           - Explain ATR and annualized volatility.
           - Interpret the supplied Bollinger Band values.
           - Describe the price position relative to the bands
             only when supported by the supplied values.
           - Do not calculate distances or percentages.

        5. RISK ANALYSIS
           - Explain current drawdown.
           - Explain maximum historical drawdown.
           - Distinguish current conditions from historical
             downside observed in the dataset.

        6. OVERALL TECHNICAL OUTLOOK
           - Summarize positive signals.
           - Summarize negative or conflicting signals.
           - Explain important risks and limitations.
           - Do not make future price predictions.

        STRICT DATA RULES:

        - Use only the supplied stock report.
        - Never invent numerical values or indicators.
        - Do not calculate additional financial statistics.
        - Do not derive new numerical values from existing values.
        - Do not estimate missing values.
        - Preserve the supplied numerical values accurately.
        - Use units only when they are provided or clearly
          established by the supplied report.
        - If information is unavailable, explicitly say so.

        NUMERICAL FORMATTING RULES:
        - Daily return, annualized volatility, current drawdown
          and maximum historical drawdown are percentage values
          in the supplied report. Display them with the % symbol.
        - Do not multiply or divide these values by 100.
        - Display RSI, ATR, MACD, moving averages and Bollinger
          Band values without adding an unsupported unit.
        - Preserve the original numerical precision where practical.

        MOMENTUM INTERPRETATION RULES:

        - A positive MACD histogram means the MACD line is
          above its signal line.
        - Do not claim that momentum is increasing, weakening,
          accelerating or slowing from a single snapshot.
        - Do not infer a crossover event from a single snapshot.
        - A negative MACD value can still be above its signal line.
        - Do not automatically classify RSI as overbought or
          oversold unless supported by the supplied interpretation.
        - Explain agreement or disagreement between indicators
          without exaggerating the strength of the signals.
        - Use the supplied RSI interpretation as the primary
          classification.
        - Do not introduce general RSI threshold explanations
          unless they are explicitly included in the report.
        - Do not describe momentum as strong, weak or extreme
          unless the supplied values and interpretations support it.

        TREND INTERPRETATION RULES:

        - Do not identify a golden cross or death cross from
          a single snapshot.
        - Do not assume a trend reversal.
        - Do not contradict the supplied trend interpretation
          without explaining the numerical evidence.
        - Distinguish the current price position relative to
          MA50 and MA200 from the supplied trend classification.
        - Explain the relationship between closing price and MA50.
        - Explain the relationship between closing price and MA200.
        - Explain whether MA50 is above or below MA200.
        - Treat these as separate observations.
        - Do not infer a trend reversal or a change in trend
          from these relationships alone.
        - Preserve the supplied trend classification.

        VOLATILITY INTERPRETATION RULES:

        - Do not classify volatility as low, moderate or high
          without a supplied benchmark or classification.
        - Do not calculate the distance between the closing
          price and either Bollinger Band.
        - Do not claim that price movement outside a band
          guarantees a reversal or continuation.
        - Do not infer changes in volatility from one snapshot.

        RISK INTERPRETATION RULES:

        - Describe drawdown using the supplied definition:
          decline from the running historical peak in the dataset.
        - Do not calculate recovery percentages.
        - Do not interpret historical drawdown as a prediction
          of future losses.
        - Clearly distinguish current drawdown from maximum
          historical drawdown.
        - Do not use exaggerated descriptions such as
          "significant risk", "severe weakness" or "extreme risk"
          unless explicitly supported by a supplied classification.
        - Do not introduce risk classifications that are absent
          from the input report.

        OUTPUT RULES:

        - Complete all six requested sections.
        - Keep the report structured and understandable.
        - Every numerical claim must match the input.
        - Do not repeat the same observation unnecessarily.
        - Explain conflicting signals rather than ignoring them.
        - Clearly distinguish supplied interpretations from
          direct observations.
        - Never provide buy or sell recommendations.
        - Never guarantee future returns.
        - Treat all indicators as historical analytical evidence.
        - End every section and sentence properly.
        - Avoid vague or speculative phrases such as
          "extended movement", "possible recovery",
          "potential reversal" and "increasing pressure"
          unless directly supported by the supplied data.
        - Prefer factual descriptions over dramatic language.
        - Do not add general market knowledge as if it were
          an observation from this stock report.
        """,

        expected_output="""
        A structured technical analysis report containing
        all six requested sections:

        1. Price Overview
        2. Momentum Analysis
        3. Trend Analysis
        4. Volatility Analysis
        5. Risk Analysis
        6. Overall Technical Outlook

        Every numerical statement must be supported by the
        supplied stock report. No unsupported calculations,
        assumptions, crossover claims or future predictions.
        """,

        agent=agent
    )

    return task


def run_technical_agent(stock_report):

    agent = create_technical_agent()
    task = create_technical_task(agent)

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=False
    )

    result = crew.kickoff(
        inputs={
            "stock_report": stock_report
        }
    )

    return result
