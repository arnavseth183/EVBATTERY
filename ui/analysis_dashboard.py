import streamlit as st
import pandas as pd

def display_analysis(metrics, backtest_results):
    """
    Display analysis metrics and backtesting results on Streamlit dashboard.
    """
    st.title("Trading Strategy Analysis")

    st.header("Performance Metrics")
    for metric, value in metrics.items():
        st.write(f"{metric}: {value}")

    st.header("Equity Curve")
    st.line_chart(backtest_results["equity"])

    st.header("Position Details")
    st.dataframe(backtest_results["positions"])

# Example usage
if __name__ == "__main__":
    # Mock data for demonstration
    metrics = {
        "Sharpe Ratio": 1.42,
        "Sortino Ratio": 1.89,
        "Total Return": "14.3%",
        "Max Drawdown": "-8.2%",
    }

    backtest_results = pd.DataFrame({
        "equity": [10000, 10200, 10400, 10300, 10500],
        "positions": [1, 1, 0, -1, 1]
    })

    display_analysis(metrics, backtest_results)