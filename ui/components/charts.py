import streamlit as st
import pandas as pd


# --------------------------------------------------
# PRICE CHART (ENHANCED)
# --------------------------------------------------

def render_price_chart(price_series):

    st.subheader("📈 Price Chart")

    if price_series is None or len(price_series) == 0:
        st.warning("No price data available")
        return

    df = pd.DataFrame(price_series)
    df.columns = ["Price"]

    # Optional smoothing toggle
    smooth = st.checkbox("Apply Moving Average", key="price_smooth")

    if smooth:
        df["SMA (10)"] = df["Price"].rolling(10).mean()

    st.line_chart(df)

    st.caption("Live price data (1-minute interval)")


# --------------------------------------------------
# PORTFOLIO ALLOCATION (IMPROVED)
# --------------------------------------------------

def render_allocation_chart(allocation):

    st.subheader("📊 Portfolio Allocation")

    if not allocation:
        st.warning("No allocation data available")
        return

    df = pd.DataFrame(list(allocation.items()), columns=["Asset", "Value"])
    df = df.set_index("Asset")

    st.bar_chart(df)

    st.caption("Current portfolio distribution")


# --------------------------------------------------
# VOLUME CHART (WITH NORMALIZATION)
# --------------------------------------------------

def render_volume_chart(volume_series):

    st.subheader("📉 Volume Analysis")

    if volume_series is None or len(volume_series) == 0:
        st.warning("No volume data available")
        return

    df = pd.DataFrame(volume_series)
    df.columns = ["Volume"]

    normalize = st.checkbox("Normalize Volume", key="volume_norm")

    if normalize:
        df["Volume"] = (df["Volume"] - df["Volume"].min()) / (
            df["Volume"].max() - df["Volume"].min()
        )

    st.area_chart(df)

    st.caption("Trading volume trends")


# --------------------------------------------------
# PNL CHART (WITH DRAWDOWN)
# --------------------------------------------------

def render_pnl_chart(pnl_series):

    st.subheader("💰 PnL Over Time")

    if pnl_series is None or len(pnl_series) == 0:
        st.warning("No PnL data available")
        return

    df = pd.DataFrame(pnl_series)
    df.columns = ["PnL"]

    # Compute drawdown
    df["Peak"] = df["PnL"].cummax()
    df["Drawdown"] = (df["PnL"] - df["Peak"]) / df["Peak"]

    show_drawdown = st.checkbox("Show Drawdown", key="pnl_drawdown")

    if show_drawdown:
        st.line_chart(df[["PnL", "Drawdown"]])
    else:
        st.line_chart(df["PnL"])

    st.caption("Profit & Loss with optional drawdown visualization")