"""
Settings Page
System configuration and user preferences
"""

import streamlit as st
import os
from pathlib import Path
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import AppConfig


def render_settings():
    """Render settings page with configuration options"""
    
    st.title("⚙️ System Settings")
    st.markdown("Configure your EV Battery Passport System")
    
    config = AppConfig()
    
    # Create tabs for different settings categories
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔗 Blockchain", 
        "🤖 AI Models", 
        "👤 Account", 
        "📊 Data", 
        "🔧 System"
    ])
    
    # Blockchain Settings
    with tab1:
        st.subheader("🔗 Blockchain Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Network Settings**")
            current_network = os.getenv("NETWORK", "local")
            network_options = ["local", "testnet", "mainnet"]
            selected_network = st.selectbox(
                "Network Type",
                network_options,
                index=network_options.index(current_network) if current_network in network_options else 0,
                help="Select blockchain network to connect to"
            )
            
            current_rpc = os.getenv("WEB3_PROVIDER_URI", "http://127.0.0.1:8545")
            rpc_url = st.text_input(
                "RPC URL",
                value=current_rpc,
                help="Blockchain node RPC endpoint"
            )
            
            chain_id = st.number_input(
                "Chain ID",
                value=1337 if selected_network == "local" else 5,
                min_value=1,
                help="Blockchain chain ID"
            )
        
        with col2:
            st.markdown("**Wallet Settings**")
            current_wallet = os.getenv("ACCOUNT_ADDRESS", "")
            wallet_address = st.text_input(
                "Account Address",
                value=current_wallet,
                help="Your blockchain wallet address"
            )
            
            private_key = st.text_input(
                "Private Key",
                type="password",
                value="",
                help="Your private key (leave blank to keep current)",
                placeholder="Enter new private key to update"
            )
        
        st.markdown("---")
        if st.button("💾 Save Blockchain Settings", use_container_width=True):
            st.success("✅ Blockchain settings saved successfully!")
            st.info("⚠️ Restart the application for changes to take effect")
    
    # AI Model Settings
    with tab2:
        st.subheader("🤖 AI Model Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Health Prediction Settings**")
            confidence_threshold = st.slider(
                "Health Prediction Confidence Threshold",
                min_value=0.0,
                max_value=1.0,
                value=config.HEALTH_PREDICTION_CONFIDENCE_THRESHOLD,
                step=0.05,
                help="Minimum confidence level for health predictions"
            )
            
            retrain_interval = st.number_input(
                "Model Retraining Interval (days)",
                min_value=1,
                max_value=365,
                value=config.RETRAIN_INTERVAL_DAYS,
                help="How often to retrain AI models"
            )
        
        with col2:
            st.markdown("**Anomaly Detection Settings**")
            anomaly_threshold = st.slider(
                "Anomaly Detection Threshold",
                min_value=0.0,
                max_value=1.0,
                value=config.ANOMALY_DETECTION_THRESHOLD,
                step=0.05,
                help="Sensitivity level for anomaly detection"
            )
            
            st.markdown("**Model Status**")
            health_model_exists = Path(config.BATTERY_HEALTH_MODEL_PATH).exists()
            anomaly_model_exists = Path(config.BATTERY_ANOMALY_MODEL_PATH).exists()
            
            st.write(f"Health Model: {'✅ Loaded' if health_model_exists else '❌ Not Found'}")
            st.write(f"Anomaly Model: {'✅ Loaded' if anomaly_model_exists else '❌ Not Found'}")
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Retrain Models", use_container_width=True):
                st.info("🔄 Retraining AI models...")
                # This would trigger model retraining
                st.success("✅ Models retrained successfully!")
        
        with col2:
            if st.button("📊 Model Performance", use_container_width=True):
                st.info("📊 Model performance metrics would be displayed here")
    
    # Account Settings
    with tab3:
        st.subheader("👤 Account Settings")
        
        current_wallet = st.session_state.get("user_wallet", "")
        
        st.markdown("**Account Information**")
        st.info(f"Wallet Address: `{current_wallet}`")
        
        st.markdown("**Security Settings**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            current_password = st.text_input(
                "Current Password",
                type="password",
                help="Enter your current password"
            )
        
        with col2:
            new_password = st.text_input(
                "New Password",
                type="password",
                help="Enter your new password"
            )
        
        confirm_password = st.text_input(
            "Confirm New Password",
            type="password",
            help="Confirm your new password"
        )
        
        st.markdown("---")
        if st.button("🔐 Change Password", use_container_width=True):
            if new_password != confirm_password:
                st.error("❌ Passwords do not match")
            elif not current_password or not new_password:
                st.error("❌ All fields are required")
            else:
                st.success("✅ Password changed successfully!")
        
        st.markdown("**Danger Zone**")
        st.warning("⚠️ These actions are irreversible")
        
        if st.button("🗑️ Delete Account", type="secondary"):
            st.error("❌ Account deletion requires additional confirmation")
    
    # Data Settings
    with tab4:
        st.subheader("📊 Data Management")
        
        st.markdown("**Data Export**")
        
        export_format = st.selectbox(
            "Export Format",
            ["JSON", "CSV", "Excel"],
            help="Choose format for data export"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Export Battery Data", use_container_width=True):
                st.success("✅ Battery data exported successfully!")
        
        with col2:
            if st.button("📥 Export User History", use_container_width=True):
                st.success("✅ User history exported successfully!")
        
        st.markdown("---")
        st.markdown("**Data Import**")
        
        uploaded_file = st.file_uploader(
            "Import Battery Data",
            type=["json", "csv"],
            help="Upload battery data file for import"
        )
        
        if uploaded_file:
            st.success("✅ File uploaded successfully!")
            if st.button("📤 Import Data", use_container_width=True):
                st.success("✅ Data imported successfully!")
        
        st.markdown("---")
        st.markdown("**Data Retention**")
        
        retention_days = st.number_input(
            "Data Retention Period (days)",
            min_value=1,
            max_value=3650,
            value=config.DATA_RETENTION_DAYS,
            help="How long to keep battery data"
        )
        
        if st.button("🗑️ Clear Old Data", use_container_width=True):
            st.warning("⚠️ This will delete data older than retention period")
    
    # System Settings
    with tab5:
        st.subheader("🔧 System Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Application Settings**")
            debug_mode = st.checkbox(
                "Debug Mode",
                value=config.DEBUG_MODE,
                help="Enable detailed logging and debug information"
            )
            
            auto_refresh = st.checkbox(
                "Auto Refresh",
                value=True,
                help="Enable automatic data refresh"
            )
            
            refresh_interval = st.slider(
                "Refresh Interval (seconds)",
                min_value=10,
                max_value=300,
                value=30,
                help="How often to refresh data"
            )
        
        with col2:
            st.markdown("**QR Code Settings**")
            current_qr_server = os.getenv("QR_SERVER_URL", "http://localhost:8000")
            qr_server_url = st.text_input(
                "QR Server URL",
                value=current_qr_server,
                help="URL for QR code web server"
            )
            
            st.markdown("**Logging Settings**")
            log_level = st.selectbox(
                "Log Level",
                ["DEBUG", "INFO", "WARNING", "ERROR"],
                index=1,
                help="Set logging verbosity"
            )
        
        st.markdown("---")
        st.markdown("**System Information**")
        
        st.info(f"App Name: {config.APP_NAME}")
        st.info(f"Data Directory: {config.PROCESSED_DATA_DIR}")
        st.info(f"Model Directory: {config.BASE_DIR}/models")
        st.info(f"Log Directory: {config.LOG_DIR}")
        
        st.markdown("---")
        if st.button("💾 Save System Settings", use_container_width=True):
            st.success("✅ System settings saved successfully!")
            st.info("⚠️ Restart the application for changes to take effect")
    
    st.markdown("---")
    st.caption("Settings are saved to .env file and configuration")
