import streamlit as st
import logging
import os
import time
import base64
import json
from pathlib import Path
from streamlit_autorefresh import st_autorefresh

from config import AppConfig
from ai_oracle.prediction.predictor import BatteryHealthPredictor
from blockchain_protocol.execution_engine.battery_passport_controller import BatteryPassportController
from blockchain_protocol.logging_config import get_app_logger

# UI pages
from ui.pages.dashboard import render_dashboard
from ui.pages.blockchain_explorer import render_blockchain_explorer
from ui.pages.add_battery import render_add_battery
from ui.pages.data_entry_selection import render_data_entry_selection, render_automatic_generation
from ui.pages.battery_records import render_battery_records
from ui.pages.user_history import render_user_history
from ui.pages.settings import render_settings

from ui.components.sidebar import render_sidebar
from blockchain_protocol.storage.user_wallet_registry import UserWalletRegistry

# 🔥 APP LOGGER FOR GENERAL EVENTS
app_logger = get_app_logger()

# --------------------------------------------------
# BATTERY PASSPORT CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="EV Battery Passport System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# SETUP
# --------------------------------------------------

config = AppConfig()

# Create necessary directories
log_dir = config.LOG_DIR
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_dir, "app.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

st_autorefresh(interval=30000, key="live_refresh")  # 30 seconds

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_wallet" not in st.session_state:
    st.session_state.user_wallet = None

if "last_data_sync" not in st.session_state:
    st.session_state.last_data_sync = 0

# --------------------------------------------------
# LOGIN SYSTEM
# --------------------------------------------------

registry = UserWalletRegistry()

if not st.session_state.logged_in:

    st.title("🔐 EV Battery Passport - Access")
    st.markdown("### Secure Login for Battery Lifecycle Management")

    tab1, tab2, tab3 = st.tabs(["🔑 Login", "📝 Create Account", "🔄 Recover Account"])

    # ============ LOGIN ============
    with tab1:
        st.subheader("User Login")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", key="login_btn", use_container_width=True):
                user = registry.authenticate_user(username, password)

                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_wallet = user["wallet_address"]
                    st.success("✅ Login successful")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")

    # ============ REGISTER ============
    with tab2:
        st.subheader("Create New Account")
        st.markdown("Create an account to manage your EV battery passport data.")
        
        username_new = st.text_input("New Username", key="reg_user")
        password_new = st.text_input("New Password", type="password", key="reg_pass")
        password_confirm = st.text_input("Confirm Password", type="password", key="reg_pass_confirm")

        if st.button("Create Account", key="reg_btn", use_container_width=True):
            if password_new != password_confirm:
                st.error("❌ Passwords do not match")
            else:
                account = registry.create_user(username_new, password_new)
                st.success("✅ Account created successfully!")
                
                with st.expander("📱 Account Details", expanded=True):
                    st.markdown("**Wallet Address:**")
                    st.code(account["wallet_address"])
                    
                    if "private_key" in account:
                        st.warning("⚠️ **IMPORTANT:** Save your private key. It cannot be recovered!")
                        st.code(account["private_key"])

    # ============ RECOVER ACCOUNT ============
    with tab3:
        st.subheader("🔑 Recover Account")
        st.markdown("Recover access to your account using your private key.")
        
        username_fp = st.text_input("Username", key="fp_user")
        private_key = st.text_input("Private Key", type="password", key="fp_key")
        new_password = st.text_input("New Password", type="password", key="fp_pass")
        new_password_confirm = st.text_input("Confirm Password", type="password", key="fp_pass_confirm")

        if st.button("Reset Password", key="fp_btn", use_container_width=True):
            if not username_fp or not private_key or not new_password:
                st.error("❌ All fields are required")
            elif new_password != new_password_confirm:
                st.error("❌ Passwords do not match")
            else:
                try:
                    success = registry.reset_password(username_fp, private_key, new_password)
                    if success:
                        st.success("✅ Password reset successful! Please login with your new password.")
                    else:
                        st.error("❌ Invalid username or private key. Access denied.")
                except Exception as e:
                    st.error(f"❌ Recovery failed: {e}")

        st.info("ℹ️ If private key is lost, account cannot be recovered.")

    st.stop()

# --------------------------------------------------
# LOAD CORE ENGINE
# --------------------------------------------------

@st.cache_resource
def load_predictor():
    return BatteryHealthPredictor(config)

@st.cache_resource
def load_protocol():
    return BatteryPassportController(config)

predictor = load_predictor()
protocol = load_protocol()

# --------------------------------------------------
# MAIN DASHBOARD LAYOUT
# --------------------------------------------------

st.markdown("""
    <style>
        .title-container {
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            color: white;
            margin-bottom: 20px;
        }
        .metric-card {
            background: #f0f2f6;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="title-container">
        <h1>🔋 EV Battery Passport System</h1>
        <p>Real-time Battery Health Monitoring & Lifecycle Tracking</p>
    </div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# BATTERY SELECTION (Load before sidebar for stats)
# --------------------------------------------------

# Load available batteries from all sources (filtered by current user)
battery_ids = []
battery_names = []
all_batteries = []
current_user_wallet = st.session_state.get("user_wallet", "")

# Load from user entered batteries (filter by current user)
user_battery_file = Path(config.PROCESSED_DATA_DIR) / "user_entered_batteries.json"
if user_battery_file.exists():
    with open(user_battery_file, 'r') as f:
        user_batteries = json.load(f)
        # Filter batteries belonging to current user
        user_batteries = [b for b in user_batteries if b.get('user_wallet') == current_user_wallet]
        all_batteries.extend(user_batteries)

# Load from auto generated batteries (filter by current user)
auto_battery_file = Path(config.PROCESSED_DATA_DIR) / "auto_generated_batteries.json"
if auto_battery_file.exists():
    with open(auto_battery_file, 'r') as f:
        auto_batteries = json.load(f)
        # Filter batteries belonging to current user
        auto_batteries = [b for b in auto_batteries if b.get('user_wallet') == current_user_wallet]
        all_batteries.extend(auto_batteries)

# Load from processed data (filter by current user)
data_file = Path(config.PROCESSED_DATA_DIR) / "battery_data_processed.json"
if data_file.exists():
    with open(data_file, 'r') as f:
        processed_batteries = json.load(f)
        # Filter batteries belonging to current user
        if isinstance(processed_batteries, list):
            processed_batteries = [b for b in processed_batteries if b.get('user_wallet') == current_user_wallet]
            all_batteries.extend(processed_batteries)

# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

with st.sidebar:
    st.title("🎯 Navigation")
    
    page = st.radio(
        "Select Module",
        [
            "📊 Dashboard",
            "➕ Add Battery",
            "🔋 Battery Records",
            "📋 Full History",
            "⛓️ Blockchain Explorer",
            "⚙️ Settings"
        ],
        key="main_navigation"
    )
    
    st.divider()
    
    # User info
    st.markdown("**👤 User Information**")
    st.info(f"Wallet: `{st.session_state.user_wallet[:10]}...`")
    
    # Quick Stats
    st.markdown("**📊 Quick Stats**")
    
    # Calculate real stats from loaded batteries
    battery_count = len(all_batteries)
    avg_health = 0
    if battery_count > 0:
        soh_values = [b.get('soh', 0) for b in all_batteries if b.get('soh')]
        if soh_values:
            avg_health = sum(soh_values) / len(soh_values)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Batteries", str(battery_count), delta="Total")
    with col2:
        st.metric("Avg Health", f"{avg_health:.1f}%", delta="Current")
    
    st.divider()
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_wallet = None
        st.rerun()

if st.sidebar.button("Logout", key="logout_btn"):
    st.session_state.logged_in = False
    st.session_state.user_wallet = None
    st.rerun()

# Create battery selection options
for bat in all_batteries[:50]:  # Limit to 50 for UI performance
    passport_id = bat.get('passport_id', f"BATT-{len(battery_ids)}")
    battery_ids.append(passport_id)
    name = f"{bat.get('manufacturer', 'Unknown')} - {bat.get('battery_type', 'Unknown')} (SoH: {bat.get('soh', 0):.1f}%)"
    battery_names.append(name)

if not battery_ids:
    battery_ids = ["demo_1"]
    battery_names = ["Demo Battery - No batteries found"]

selected_battery_idx = st.sidebar.selectbox(
    "Select Battery",
    range(len(battery_names)),
    format_func=lambda x: battery_names[x],
    key="battery_select"
)

# Ensure selected_battery_idx is never None
if selected_battery_idx is None:
    selected_battery_idx = 0

selected_battery = battery_ids[selected_battery_idx] if selected_battery_idx < len(battery_ids) else "demo_1"

# --------------------------------------------------
# BATTERY HEALTH MONITORING
# --------------------------------------------------

# Default battery health
battery_health = {
    "soh": 0.0,
    "soc": 0.0,
    "temperature": 0.0,
    "health_status": "UNKNOWN",
    "temperature_status": "UNKNOWN",
    "confidence": 0.0
}

# Load actual battery data if available
if selected_battery_idx < len(all_batteries):
    bat = all_batteries[selected_battery_idx]
    
    # Calculate health status dynamically if not present
    soh = bat.get("soh", 0)
    if soh >= 90:
        health_status = "EXCELLENT"
    elif soh >= 80:
        health_status = "GOOD"
    elif soh >= 70:
        health_status = "FAIR"
    elif soh >= 60:
        health_status = "DEGRADED"
    else:
        health_status = "POOR"
    
    # Calculate temperature status dynamically
    temperature = bat.get("temperature_celsius", 0)
    if 15 <= temperature <= 35:
        temp_status = "OPTIMAL"
    elif temperature <= 50:
        temp_status = "WARNING"
    else:
        temp_status = "CRITICAL"
    
    battery_health = {
        "soh": soh,
        "soc": bat.get("soc", 0),
        "temperature": temperature,
        "health_status": health_status,
        "temperature_status": temp_status,
        "confidence": 0.85,  # Default confidence for loaded data
        "passport_id": bat.get("passport_id", selected_battery),
        "manufacturer": bat.get("manufacturer", "Unknown"),
        "battery_type": bat.get("battery_type", "Unknown"),
        "total_cycles": bat.get("total_cycles", 0),
        "capacity_kwh": bat.get("capacity_kwh", 0)
    }

logging.info(f"Battery {selected_battery} health monitored: SoH={battery_health['soh']:.1f}%")

# --------------------------------------------------
# DATA MODE SELECTION
# --------------------------------------------------

data_mode = st.sidebar.selectbox(
    "Data Source",
    ["Local", "Live"],
    key="data_mode_select"
)

# --------------------------------------------------
# PAGE ROUTING (FINAL)
# --------------------------------------------------

if page == "📊 Dashboard":
    render_dashboard(
        predictor, protocol, battery_health, selected_battery, data_mode,
        current_user=st.session_state.get("user_wallet")
    )

elif page == "➕ Add Battery":
    # Check if user has selected data entry mode
    if st.session_state.get("data_entry_mode") == "automatic":
        render_automatic_generation()
    elif st.session_state.get("data_entry_mode") == "manual":
        render_add_battery()
    else:
        render_data_entry_selection()

elif page == "🔋 Battery Records":
    render_battery_records()

elif page == "📋 Full History":
    render_user_history()

elif page == "⛓️ Blockchain Explorer":
    render_blockchain_explorer(
        protocol.get_transaction_history(),
        st.session_state.get("user_wallet")
    )

elif page == "⚙️ Settings":
    render_settings()

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("---")
st.caption("EV Battery Passport System | Capstone Project")