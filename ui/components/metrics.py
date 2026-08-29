import streamlit as st


# --------------------------------------------------
# GENERIC METRIC DISPLAY (ENHANCED)
# --------------------------------------------------

def display_metric(title, value, delta=None, is_currency=False, is_percent=False):

    # Formatting
    if is_currency:
        value = f"₹ {value:,.2f}"
    elif is_percent:
        value = f"{value:.2f}%"
    else:
        value = f"{value}"

    if delta is not None:
        if is_percent:
            delta = f"{delta:.2f}%"
        else:
            delta = f"{delta}"

    st.metric(
        label=title,
        value=value,
        delta=delta
    )


# --------------------------------------------------
# PROTOCOL METRICS (SMART VERSION)
# --------------------------------------------------

def display_protocol_metrics(protocol_state):

    st.subheader("⚙️ Protocol Metrics")

    if not protocol_state:
        st.warning("No protocol data available")
        return

    # Safe extraction
    total_trades = protocol_state.get("trades", 0)
    active_positions = protocol_state.get("positions", 0)
    treasury = protocol_state.get("treasury", 0)

    # Optional previous values for delta (if available)
    prev_trades = protocol_state.get("prev_trades")
    prev_positions = protocol_state.get("prev_positions")
    prev_treasury = protocol_state.get("prev_treasury")

    col1, col2, col3 = st.columns(3)

    with col1:
        delta_trades = None
        if prev_trades is not None:
            delta_trades = total_trades - prev_trades

        display_metric("Total Trades", total_trades, delta_trades)

    with col2:
        delta_positions = None
        if prev_positions is not None:
            delta_positions = active_positions - prev_positions

        display_metric("Active Positions", active_positions, delta_positions)

    with col3:
        delta_treasury = None
        if prev_treasury is not None:
            delta_treasury = treasury - prev_treasury

        display_metric("Treasury Balance", treasury, delta_treasury, is_currency=True)

    # --------------------------------------------------
    # INSIGHT SECTION (IMPORTANT FOR DEMO)
    # --------------------------------------------------

    st.markdown("### 📊 System Insight")

    if total_trades == 0:
        st.info("No trades executed yet")
    elif active_positions == 0:
        st.warning("No active positions — strategy may be idle")
    elif treasury < 0:
        st.error("Treasury deficit detected")
    else:
        st.success("System operating normally")

    st.markdown("---")