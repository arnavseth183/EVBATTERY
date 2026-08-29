"""
Battery Records Page with QR Code Viewing
Allows users to view all their battery records and associated QR codes
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from PIL import Image
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from blockchain_protocol.execution_engine.battery_passport_controller import BatteryPassportController
from config import AppConfig


def render_battery_records():
    """Render the battery records page with QR code viewing"""
    
    st.title("🔋 Battery Records & QR Codes")
    st.markdown("View and manage your EV battery passport records")
    
    # Initialize battery passport controller for blockchain registration
    try:
        config = AppConfig()
        protocol = BatteryPassportController(config)
    except Exception as e:
        st.warning(f"Blockchain controller initialization failed: {e}")
        protocol = None
    
    # Load all battery records (filtered by current user)
    all_batteries = []
    current_user_wallet = st.session_state.get("user_wallet", "")
    
    # Load from user entered batteries (filter by current user)
    user_battery_file = Path("data/processed/user_entered_batteries.json")
    if user_battery_file.exists():
        with open(user_battery_file, 'r') as f:
            user_batteries = json.load(f)
            # Filter batteries belonging to current user
            user_batteries = [b for b in user_batteries if b.get('user_wallet') == current_user_wallet]
            all_batteries.extend(user_batteries)
    
    # Load from auto generated batteries (filter by current user)
    auto_battery_file = Path("data/processed/auto_generated_batteries.json")
    if auto_battery_file.exists():
        with open(auto_battery_file, 'r') as f:
            auto_batteries = json.load(f)
            # Filter batteries belonging to current user
            auto_batteries = [b for b in auto_batteries if b.get('user_wallet') == current_user_wallet]
            all_batteries.extend(auto_batteries)
    
    if not all_batteries:
        st.info("📭 No battery records found. Add batteries using the 'Add Battery' page.")
        return
    
    st.success(f"📊 Found {len(all_batteries)} battery record(s)")
    
    # Search and filter
    st.markdown("---")
    st.subheader("🔍 Search & Filter")
    
    col1, col2 = st.columns(2)
    
    with col1:
        search_term = st.text_input("Search by Passport ID, Manufacturer, or Type")
    
    with col2:
        health_filter = st.selectbox(
            "Filter by Health Status",
            ["All", "EXCELLENT", "GOOD", "FAIR", "DEGRADED", "POOR"]
        )
    
    # Apply filters
    filtered_batteries = all_batteries
    
    if search_term:
        search_term = search_term.lower()
        filtered_batteries = [
            b for b in filtered_batteries
            if search_term in str(b.get("passport_id", "")).lower() or
               search_term in str(b.get("manufacturer", "")).lower() or
               search_term in str(b.get("battery_type", "")).lower()
        ]
    
    if health_filter != "All":
        filtered_batteries = [
            b for b in filtered_batteries
            if b.get("health_status") == health_filter
        ]
    
    st.info(f"Showing {len(filtered_batteries)} of {len(all_batteries)} records")
    
    # Display records
    st.markdown("---")
    st.subheader("📋 Battery Records")
    
    for idx, battery in enumerate(filtered_batteries):
        passport_id = battery.get("passport_id", "UNKNOWN")
        
        with st.expander(f"🔋 {passport_id} - {battery.get('manufacturer', 'Unknown')} {battery.get('battery_type', 'Unknown')}", expanded=(idx == 0)):
            
            # Basic information
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("SoH", f"{battery.get('soh', 0):.1f}%")
                st.metric("SoC", f"{battery.get('soc', 0):.1f}%")
            
            with col2:
                st.metric("Temperature", f"{battery.get('temperature_celsius', 0):.1f}°C")
                st.metric("Cycles", battery.get('total_cycles', 0))
            
            with col3:
                st.metric("Capacity", f"{battery.get('capacity_kwh', 0):.1f} kWh")
                st.metric("Health Status", battery.get('health_status', 'UNKNOWN'))
            
            # Detailed information
            st.markdown("**Details:**")
            details_col1, details_col2 = st.columns(2)
            
            with details_col1:
                st.write(f"**Manufacturer:** {battery.get('manufacturer', 'Unknown')}")
                st.write(f"**Battery Type:** {battery.get('battery_type', 'Unknown')}")
                st.write(f"**Production Date:** {battery.get('production_date', 'Unknown')}")
            
            with details_col2:
                st.write(f"**Passport ID:** {passport_id}")
                st.write(f"**Data Source:** {battery.get('data_source', 'Unknown')}")
                st.write(f"**Created:** {battery.get('timestamp', 'Unknown')}")
            
            # QR Code section
            st.markdown("---")
            st.markdown("**📱 QR Code:**")
            
            try:
                from utils.qr_generator import QRCodeGenerator
                qr_generator = QRCodeGenerator()
                
                # Generate QR code on the fly
                qr_result = qr_generator.create_qr_with_overlay(battery, "EV BATTERY PASSPORT")
                
                if isinstance(qr_result, dict):
                    qr_full_path = qr_result.get("overlay_path")
                    qr_url = qr_result.get("qr_url", "")
                    decoded_message = qr_result.get("decoded_message", "")
                else:
                    qr_full_path = qr_result
                    qr_url = ""
                    decoded_message = ""
                
                if qr_full_path and Path(qr_full_path).exists():
                    qr_img_full = Image.open(qr_full_path)
                    col_qr1, col_qr2 = st.columns([1, 2])
                    
                    with col_qr1:
                        st.image(qr_img_full, caption=f"Complete Battery Record - {passport_id}", use_container_width=True)
                    
                    with col_qr2:
                        st.success("✅ QR Code Generated")
                        
                        # Display decoded message
                        if decoded_message:
                            st.markdown("**📋 Decoded QR Message:**")
                            st.code(decoded_message, language="text")
                        
                        # Add button to open in new tab
                        if qr_url:
                            st.markdown(f"[🔗 Open Battery Record in New Tab]({qr_url})")
                        
                        st.info("📱 This QR code contains complete battery information. Scan to view all details.")
                else:
                    st.warning("⚠️ QR Code generation failed. Please try again.")
            except Exception as e:
                st.warning(f"Could not generate QR code: {e}")
            
            # Action buttons
            st.markdown("**Actions:**")
            col_action1, col_action2, col_action3 = st.columns(3)
            
            # Generate unique keys using index
            unique_key = f"{passport_id}_{idx}"
            
            with col_action1:
                if st.button(f"📋 Copy ID", key=f"copy_{unique_key}"):
                    st.code(passport_id)
                    st.success("Passport ID copied!")
            
            with col_action2:
                if st.button(f"📊 View Details", key=f"details_{unique_key}"):
                    st.json(battery)
            
            with col_action3:
                if st.button(f"🔗 Register on Blockchain", key=f"blockchain_{unique_key}"):
                    if protocol:
                        with st.spinner("Registering on blockchain..."):
                            result = protocol.register_on_blockchain(passport_id)
                            if result.get("status") == "SUCCESS":
                                st.success(f"✅ Battery registered on blockchain!")
                                st.info(f"Transaction Hash: {result.get('tx_hash', 'N/A')}")
                                st.info(f"Mode: {result.get('mode', 'SIMULATION')}")
                            else:
                                st.error(f"❌ Registration failed: {result.get('error', 'Unknown error')}")
                    else:
                        st.error("❌ Blockchain controller not available")
    
    # Export functionality
    st.markdown("---")
    st.subheader("📤 Export Data")
    
    col_export1, col_export2 = st.columns(2)
    
    with col_export1:
        if st.button("📄 Export as JSON"):
            st.download_button(
                label="Download JSON",
                data=json.dumps(filtered_batteries, indent=2),
                file_name=f"battery_records_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col_export2:
        if st.button("📊 Export as CSV"):
            df = pd.DataFrame(filtered_batteries)
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"battery_records_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
