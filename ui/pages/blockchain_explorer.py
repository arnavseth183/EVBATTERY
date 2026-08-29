"""
Blockchain Explorer for EV Battery Passport System
Displays battery passport blockchain registrations and transactions
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from blockchain_protocol.execution_engine.battery_passport_controller import BatteryPassportController
from config import AppConfig


def render_blockchain_explorer(tx_history, current_user):
    """Render blockchain explorer for battery passport registrations"""
    
    st.title("⛓ Blockchain Explorer - Battery Passport Registrations")
    st.markdown("View EV battery passport registrations on blockchain")
    
    # Initialize battery passport controller
    try:
        config = AppConfig()
        protocol = BatteryPassportController(config)
    except Exception as e:
        st.error(f"Failed to initialize blockchain controller: {e}")
        return
    
    # Load battery passport registrations
    battery_passport_file = Path("data/processed/battery_passports.json")
    
    if not battery_passport_file.exists():
        st.info("📭 No battery passport registrations found yet.")
        st.info("Register batteries on the 'Battery Records' page to see them here.")
        return
    
    try:
        with open(battery_passport_file, 'r') as f:
            content = f.read().strip()
            if content:
                battery_passports = json.loads(content)
            else:
                battery_passports = {}
    except Exception as e:
        st.error(f"Failed to load battery passports: {e}")
        return
    
    if not battery_passports:
        st.info("📭 No battery passport registrations found yet.")
        return
    
    # Filter by current user if specified
    if current_user:
        battery_passports = {
            pid: data for pid, data in battery_passports.items()
            if data.get("user_wallet") == current_user
        }
    
    if not battery_passports:
        st.info(f"No registrations found for user: {current_user}")
        return
    
    # Summary metrics
    st.subheader("📊 Registration Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Registrations", len(battery_passports))
    
    with col2:
        registered_count = sum(1 for b in battery_passports.values() if b.get("blockchain_registered", False))
        st.metric("Blockchain Registered", registered_count)
    
    with col3:
        simulation_count = sum(1 for b in battery_passports.values() if b.get("blockchain_registered", False))
        st.metric("Simulation Mode", simulation_count)
    
    with col4:
        unique_manufacturers = len(set(b.get("manufacturer", "Unknown") for b in battery_passports.values()))
        st.metric("Manufacturers", unique_manufacturers)
    
    st.markdown("---")
    
    # Detailed registrations view
    st.subheader("🔋 Battery Passport Registrations")
    
    # Convert to DataFrame for display
    registration_data = []
    for passport_id, battery in battery_passports.items():
        registration_data.append({
            "Passport ID": passport_id,
            "Manufacturer": battery.get("manufacturer", "Unknown"),
            "Battery Type": battery.get("battery_type", "Unknown"),
            "SoH (%)": battery.get("soh", 0),
            "Cycles": battery.get("total_cycles", 0),
            "Blockchain Registered": battery.get("blockchain_registered", False),
            "Transaction Hash": battery.get("blockchain_tx", "N/A"),
            "Registered At": battery.get("blockchain_registered_at", "N/A"),
            "Mode": "SIMULATION" if battery.get("blockchain_tx", "").startswith("0xBATT") else "LIVE"
        })
    
    df = pd.DataFrame(registration_data)
    
    # Display table
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Detailed view for each registration
    st.markdown("---")
    st.subheader("📝 Detailed Registration View")
    
    for passport_id, battery in battery_passports.items():
        with st.expander(f"🔋 {passport_id} - {battery.get('manufacturer', 'Unknown')} {battery.get('battery_type', 'Unknown')}"):
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Battery Information:**")
                st.write(f"**Passport ID:** {passport_id}")
                st.write(f"**Manufacturer:** {battery.get('manufacturer', 'Unknown')}")
                st.write(f"**Battery Type:** {battery.get('battery_type', 'Unknown')}")
                st.write(f"**Capacity:** {battery.get('capacity_kwh', 0)} kWh")
                st.write(f"**Production Date:** {battery.get('production_date', 'Unknown')}")
            
            with col2:
                st.markdown("**Health Metrics:**")
                st.write(f"**SoH:** {battery.get('soh', 0)}%")
                st.write(f"**SoC:** {battery.get('soc', 0)}%")
                st.write(f"**Total Cycles:** {battery.get('total_cycles', 0)}")
                st.write(f"**Temperature:** {battery.get('temperature_celsius', 0)}°C")
                st.write(f"**Health Status:** {battery.get('health_status', 'UNKNOWN')}")
            
            st.markdown("---")
            st.markdown("**Blockchain Registration Details:**")
            
            if battery.get("blockchain_registered", False):
                st.success("✅ Registered on Blockchain")
                st.write(f"**Transaction Hash:** `{battery.get('blockchain_tx', 'N/A')}`")
                st.write(f"**Registered At:** {battery.get('blockchain_registered_at', 'N/A')}")
                st.write(f"**Mode:** {'SIMULATION' if battery.get('blockchain_tx', '').startswith('0xBATT') else 'LIVE'}")
            else:
                st.warning("⚠️ Not registered on blockchain")
                st.info("Register this battery on the 'Battery Records' page")
    
    st.markdown("---")
    st.caption("Battery passport registrations are stored on blockchain for immutability and traceability. In simulation mode, transactions are generated locally for demonstration purposes.")


# Test run
if __name__ == "__main__":
    render_blockchain_explorer([], current_user=None)