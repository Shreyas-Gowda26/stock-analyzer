
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import json
from pathlib import Path
from src.agents.stock_analysis import run_stock_analysis
# -----------------------------
# Page configuration
# -----------------------------

st.set_page_config(
    page_title="Indian Stock Market Analysis",
    page_icon="📈",
    layout="wide"
)


# -----------------------------
# Dashboard styling
# -----------------------------

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        h1 {
            letter-spacing: -1px;
        }

        div[data-testid="stMetric"] {
            background-color: rgba(128, 128, 128, 0.08);
            border: 1px solid rgba(128, 128, 128, 0.2);
            padding: 18px;
            border-radius: 12px;
        }

        div[data-testid="stSelectbox"] {
            margin-bottom: 0.5rem;
        }

        hr {
            margin-top: 1.5rem;
            margin-bottom: 1.5rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Load data
# -----------------------------

DATA_FILE = "data/processed/indian_stocks_clean.csv"
MONTHLY_FILE = "data/processed/indian_stocks_monthly.csv"

df = pd.read_csv(DATA_FILE)
df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values(["Ticker", "Date"])

monthly_df = pd.read_csv(MONTHLY_FILE)
monthly_df["Date"] = pd.to_datetime(monthly_df["Date"])
monthly_df = monthly_df.sort_values(["Ticker", "Date"])

# -----------------------------
# Load AI analysis reports
# -----------------------------

TECHNICAL_REPORT_FILE = Path(
    "data/processed/technical_reports.json"
)

RISK_REPORT_FILE = Path(
    "data/processed/risk_reports.json"
)

with TECHNICAL_REPORT_FILE.open("r") as file:
    technical_reports = json.load(file)

with RISK_REPORT_FILE.open("r") as file:
    risk_reports = json.load(file)
# -----------------------------
# Title
# -----------------------------

st.title("📈 Indian Stock Market Analysis")

st.write(
    "Interactive analysis of selected Indian stocks "
    "using historical market data."
)


# -----------------------------
# Stock selector
# -----------------------------

stocks = sorted(df["Ticker"].unique())

selected_stock = st.selectbox("Select a stock", stocks)

stock_df = (
    df[df["Ticker"] == selected_stock]
    .copy()
    .sort_values("Date")
)


# -----------------------------
# Basic information
# -----------------------------

latest_price = stock_df["Close"].iloc[-1]
start_date = stock_df["Date"].min().date()
end_date = stock_df["Date"].max().date()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Selected Stock", selected_stock)

with col2:
    st.metric("Latest Closing Price", f"₹{latest_price:.2f}")

with col3:
    st.metric("Data Period", f"{start_date} → {end_date}")


# -----------------------------
# Chart helper
# -----------------------------

def add_chart(
    data,
    chart_type,
    x,
    y,
    name,
    color=None,
    fill=None
):
    """Add the selected chart type to the current Plotly figure."""

    if chart_type == "Line Chart":
        fig.add_trace(
            go.Scatter(
                x=data[x],
                y=data[y],
                mode="lines",
                name=name,
                line=dict(color=color) if color else None
            )
        )

    elif chart_type == "Area Chart":
        fig.add_trace(
            go.Scatter(
                x=data[x],
                y=data[y],
                mode="lines",
                fill=fill or "tozeroy",
                name=name,
                line=dict(color=color) if color else None
            )
        )

    elif chart_type == "Bar Chart":
        fig.add_trace(
            go.Bar(
                x=data[x],
                y=data[y],
                name=name,
                marker_color=color
            )
        )


# -----------------------------
# Stock Price Trend
# -----------------------------

st.subheader("Stock Price Trend")

price_type = st.selectbox(
    "Choose price chart type",
    ["Line Chart", "Area Chart", "Candlestick Chart", "Bar Chart"],
    key="price_chart_type"
)

fig = go.Figure()

if price_type == "Candlestick Chart":
    fig.add_trace(
        go.Candlestick(
            x=stock_df["Date"],
            open=stock_df["Open"],
            high=stock_df["High"],
            low=stock_df["Low"],
            close=stock_df["Close"],
            name="OHLC"
        )
    )

else:
    add_chart(
        stock_df, price_type, "Date", "Close", "Closing Price"
    )

    if price_type == "Line Chart":
        add_chart(
            stock_df, "Line Chart", "Date", "MA50", "MA50"
        )
        add_chart(
            stock_df, "Line Chart", "Date", "MA200", "MA200"
        )

fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Price (₹)",
    hovermode="x unified",
    legend_title="Indicator",
    xaxis_rangeslider_visible=(price_type == "Candlestick Chart")
)

st.plotly_chart(fig, width="stretch")


# -----------------------------
# Daily Returns
# -----------------------------

st.subheader("Daily Returns")

returns_type = st.selectbox(
    "Choose returns chart type",
    ["Line Chart", "Bar Chart", "Area Chart"],
    key="returns_chart_type"
)

returns_df = stock_df.dropna(subset=["Daily_Return"]).copy()
returns_df["Daily_Return_Percent"] = returns_df["Daily_Return"] * 100

fig = go.Figure()

add_chart(
    returns_df,
    returns_type,
    "Date",
    "Daily_Return_Percent",
    "Daily Return (%)"
)

fig.add_hline(y=0, line_dash="dash")

fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Daily Return (%)",
    hovermode="x unified"
)

st.plotly_chart(fig, width="stretch")


# -----------------------------
# Trading Volume
# -----------------------------

st.subheader("Trading Volume")

volume_type = st.selectbox(
    "Choose volume chart type",
    ["Bar Chart", "Line Chart", "Area Chart"],
    key="volume_chart_type"
)

fig = go.Figure()

add_chart(
    stock_df,
    volume_type,
    "Date",
    "Volume",
    "Trading Volume"
)

fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Volume (shares)",
    hovermode="x unified"
)

st.plotly_chart(fig, width="stretch")


# -----------------------------
# Monthly Performance Comparison
# -----------------------------

st.subheader("Monthly Performance Comparison")

monthly_type = st.selectbox(
    "Choose monthly chart type",
    ["Line Chart", "Bar Chart", "Area Chart"],
    key="monthly_chart_type"
)

monthly_fig = go.Figure()

for stock in sorted(monthly_df["Ticker"].unique()):
    stock_monthly = monthly_df[
        monthly_df["Ticker"] == stock
    ].sort_values("Date").copy()

    stock_monthly["Monthly_Return_Percent"] = (
        stock_monthly["Monthly_Return"] * 100
    )

    if monthly_type == "Line Chart":
        monthly_fig.add_trace(
            go.Scatter(
                x=stock_monthly["Date"],
                y=stock_monthly["Monthly_Return_Percent"],
                mode="lines+markers",
                name=stock
            )
        )

    elif monthly_type == "Bar Chart":
        monthly_fig.add_trace(
            go.Bar(
                x=stock_monthly["Date"],
                y=stock_monthly["Monthly_Return_Percent"],
                name=stock
            )
        )

    elif monthly_type == "Area Chart":
        monthly_fig.add_trace(
            go.Scatter(
                x=stock_monthly["Date"],
                y=stock_monthly["Monthly_Return_Percent"],
                mode="lines",
                name=stock,
                stackgroup=None
            )
        )

monthly_fig.add_hline(y=0, line_dash="dash")

monthly_fig.update_layout(
    xaxis_title="Month",
    yaxis_title="Monthly Return (%)",
    hovermode="x unified",
    legend_title="Stock",
    barmode="group" if monthly_type == "Bar Chart" else "overlay"
)

st.plotly_chart(monthly_fig, width="stretch")


# -----------------------------
# Stock Summary
# -----------------------------

st.subheader("Stock Summary")

summary = (
    df.groupby("Ticker")
    .agg(
        Latest_Price=("Close", "last"),
        Average_Daily_Return=("Daily_Return", "mean"),
        Average_Volume=("Volume", "mean")
    )
    .reset_index()
)

summary["Average_Daily_Return"] *= 100

summary = summary.rename(
    columns={
        "Ticker": "Stock",
        "Latest_Price": "Latest Price (₹)",
        "Average_Daily_Return": "Avg Daily Return (%)",
        "Average_Volume": "Avg Trading Volume"
    }
)

st.dataframe(
    summary.style.format({
        "Latest Price (₹)": "₹{:,.2f}",
        "Avg Daily Return (%)": "{:.3f}%",
        "Avg Trading Volume": "{:,.0f}"
    }),
    width="stretch",
    hide_index=True
)


# -----------------------------
# AI Stock Analysis
# -----------------------------

st.divider()

st.header("🤖 AI Stock Analysis")

st.write(
    "Technical and risk assessment of the selected stock "
    "using calculated market indicators."
)

# Find reports for selected stock

technical_report = next(
    (
        report for report in technical_reports
        if report["ticker"] == selected_stock
    ),
    None
)

risk_report = next(
    (
        report for report in risk_reports
        if report["ticker"] == selected_stock
    ),
    None
)

if technical_report and risk_report:

    # Overall Risk
    st.subheader("Overall Risk Assessment")

    overall_risk = risk_report["overall_risk"]

    st.metric(
        label="Overall Risk Level",
        value=overall_risk
    )

    # Technical Analysis
    st.subheader("Technical Analysis")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "RSI",
            f'{technical_report["momentum"]["rsi"]:.2f}'
        )

    with col2:
        st.metric(
            "MACD",
            f'{technical_report["momentum"]["macd"]:.2f}'
        )

    with col3:
        st.metric(
            "Annualized Volatility",
            f'{risk_report["volatility"]["annualized_volatility"]:.2f}%'
        )

    st.write(
        "**Trend:**",
        technical_report["trend"]["interpretation"]
    )

    st.write(
        "**RSI Interpretation:**",
        technical_report["momentum"]["rsi_signal"]
    )

    st.write(
        "**MACD Interpretation:**",
        technical_report["momentum"]["macd_interpretation"]
    )

    # Risk Analysis
    st.subheader("Risk Analysis")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Volatility Risk",
            risk_report["volatility"]["risk_level"]
        )

    with col2:
        st.metric(
            "Current Drawdown Risk",
            risk_report["drawdown"]["current_risk_level"]
        )

    with col3:
        st.metric(
            "Historical Drawdown Risk",
            risk_report["drawdown"]["historical_risk_level"]
        )

    st.write(
        "**Current Drawdown:**",
        f'{risk_report["drawdown"]["current_drawdown"]:.2f}%'
    )

    st.write(
        "**Maximum Historical Drawdown:**",
        f'{risk_report["drawdown"]["maximum_historical_drawdown"]:.2f}%'
    )

else:
    st.warning(
        "Technical or risk report is unavailable for this stock."
    )


# -----------------------------
# On-Demand AI Stock Analysis
# -----------------------------

st.divider()

st.header("🧠 AI Stock Analysis")

st.write(
    "Select the AI analyst you need and generate "
    "an analysis for the selected stock."
)

# Select AI agents
selected_agents = st.multiselect(
    "Choose AI Analyst(s)",
    options=["technical", "risk"],
    default=["technical"],
    format_func=lambda x: {
        "technical": "📊 Technical Analyst",
        "risk": "⚠️ Risk Analyst"
    }[x]
)

# Generate analysis on button click
if st.button(
    "🚀 Generate AI Analysis",
    type="primary",
    disabled=len(selected_agents) == 0
):

    try:
        with st.spinner(
            f"Generating analysis for {selected_stock}..."
        ):

            ai_report = run_stock_analysis(
                ticker=selected_stock,
                selected_agents=selected_agents
            )

            st.session_state[
                f"ai_report_{selected_stock}"
            ] = ai_report

        st.success("AI analysis generated successfully!")

    except Exception as e:
        st.error(f"Analysis failed: {e}")


# -----------------------------
# Display Generated Analysis
# -----------------------------

report_file = Path(
    "data/processed/final_reports"
) / f"{selected_stock.replace('.', '_')}.json"

ai_report = None

if report_file.exists():

    with report_file.open("r") as file:
        ai_report = json.load(file)

if ai_report:

    st.caption(
        f"Analysis report for {selected_stock} "
        f" | Data date: {ai_report['date']}"
    )

    if ai_report.get("technical_analysis"):

        with st.expander(
            "📊 AI Technical Analyst",
            expanded=True
        ):
            st.markdown(
                ai_report["technical_analysis"]
            )

    if ai_report.get("risk_analysis"):

        with st.expander(
            "⚠️ AI Risk Analyst",
            expanded=False
        ):
            st.markdown(
                ai_report["risk_analysis"]
            )

    st.caption(
        "Disclaimer: AI-generated analysis is for educational "
        "and informational purposes only. It is not financial advice."
    )

else:

    st.info(
        f"No AI analysis generated yet for {selected_stock}. "
        "Choose an analyst and click Generate AI Analysis."
    )


