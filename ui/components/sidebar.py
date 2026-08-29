import streamlit as st


def render_sidebar():

    st.sidebar.title("⚙️ DABTP Control Panel")

    st.sidebar.markdown("---")

    # --------------------------------------------------
    # NAVIGATION (UPDATED)
    # --------------------------------------------------

    page = st.sidebar.radio(
        "📍 Navigation",
        [
            "Dashboard",
            "Trade Panel",
            "Portfolio",
            "Blockchain Explorer",
            "Risk Dashboard",   # ✅ ADDED
            "Governance"        # ✅ ADDED
        ],
        key="nav_page"
    )

    st.sidebar.markdown("---")

    # --------------------------------------------------
    # DATA SOURCE
    # --------------------------------------------------

    data_mode = st.sidebar.radio(
        "📡 Data Source",
        ["LIVE", "SIMULATED"],
        key="data_mode"
    )

    # --------------------------------------------------
    # EXECUTION MODE
    # --------------------------------------------------

    execution_mode = st.sidebar.radio(
        "⚡ Execution Mode",
        ["MANUAL", "AUTO"],
        key="exec_mode"
    )

    st.sidebar.markdown("---")

    # --------------------------------------------------
    # SYSTEM STATUS (DYNAMIC)
    # --------------------------------------------------

    st.sidebar.subheader("🟢 System Status")

    # These can later be wired to real health checks
    st.sidebar.success("Blockchain Connected")
    st.sidebar.success("AI Oracle Active")

    if execution_mode == "AUTO":
        st.sidebar.info("Auto Trading Enabled")
    else:
        st.sidebar.warning("Manual Mode Active")

    # --------------------------------------------------
    # QUICK INFO PANEL (VERY USEFUL)
    # --------------------------------------------------

    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Quick Info")

    st.sidebar.write(f"Mode: {execution_mode}")
    st.sidebar.write(f"Data: {data_mode}")

    # --------------------------------------------------
    # FOOTER
    # --------------------------------------------------

    st.sidebar.markdown("---")
    st.sidebar.caption("Decentralized AI-Blockchain Trading System")

    # --------------------------------------------------
    # RETURN (UNCHANGED)
    # --------------------------------------------------

    return page, data_mode, execution_mode