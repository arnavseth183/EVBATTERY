"""
Battery Data Entry Page
Streamlit interface for manual battery data entry
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.battery_data_loader import BatteryDataLoader
from ai_oracle.prediction.predictor import Predictor
from utils.qr_generator import QRCodeGenerator


def render_add_battery():
    """Render the add battery page."""
    
    st.title("🔋 Add New Battery Record")
    st.markdown("---")
    
    # Initialize data loader
    data_loader = BatteryDataLoader()
    
    # Create form
    with st.form("battery_form", clear_on_submit=True):
        st.subheader("📝 Battery Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Battery Type
            battery_type = st.selectbox(
                "Battery Type",
                options=data_loader.config["battery_types"] + ["Other"],
                help="Select the battery chemistry type"
            )
            
            if battery_type == "Other":
                battery_type = st.text_input("Enter custom battery type")
            
            # Manufacturer
            manufacturers = ["Tesla", "BYD", "LG", "Panasonic", "Samsung", "CATL", "Other"]
            manufacturer = st.selectbox(
                "Manufacturer",
                options=manufacturers,
                help="Select the battery manufacturer"
            )
            
            if manufacturer == "Other":
                manufacturer = st.text_input("Enter manufacturer name")
        
        with col2:
            # Capacity
            capacity_kwh = st.number_input(
                "Battery Capacity (kWh)",
                min_value=50.0,
                max_value=150.0,
                value=75.0,
                step=0.5,
                help="Total battery capacity in kilowatt-hours"
            )
            
            # Production Date
            prod_date = st.date_input(
                "Production Date",
                value=datetime.now(),
                help="Battery manufacturing date"
            )
        
        st.subheader("📊 Current Status")
        
        col3, col4, col5 = st.columns(3)
        
        with col3:
            soh = st.slider(
                "State of Health (SoH) %",
                min_value=0.0,
                max_value=100.0,
                value=85.0,
                step=0.1,
                help="Battery capacity retention percentage (0-100%)"
            )
        
        with col4:
            soc = st.slider(
                "State of Charge (SoC) %",
                min_value=0.0,
                max_value=100.0,
                value=60.0,
                step=0.1,
                help="Current charge level (0-100%)"
            )
        
        with col5:
            total_cycles = st.number_input(
                "Total Cycles",
                min_value=0,
                max_value=10000,
                value=500,
                step=1,
                help="Number of charge-discharge cycles"
            )
        
        st.subheader("🌡️ Environment & Conditions")
        
        col6, col7 = st.columns(2)
        
        with col6:
            temperature = st.slider(
                "Temperature (°C)",
                min_value=10.0,
                max_value=60.0,
                value=28.0,
                step=0.5,
                help="Current operating temperature"
            )
        
        with col7:
            # Calculate degradation
            degradation_per_cycle = (100 - soh) / max(total_cycles, 1)
            st.metric("Degradation/Cycle", f"{degradation_per_cycle:.4f}%")
        
        # Calculate health status
        thresholds = data_loader.config["health_thresholds"]
        if thresholds["excellent"][0] <= soh <= thresholds["excellent"][1]:
            health_status = "EXCELLENT"
            status_color = "🟢"
        elif thresholds["good"][0] <= soh <= thresholds["good"][1]:
            health_status = "GOOD"
            status_color = "🟢"
        elif thresholds["fair"][0] <= soh <= thresholds["fair"][1]:
            health_status = "FAIR"
            status_color = "🟡"
        elif thresholds["degraded"][0] <= soh <= thresholds["degraded"][1]:
            health_status = "DEGRADED"
            status_color = "🟠"
        else:
            health_status = "POOR"
            status_color = "🔴"
        
        # Temperature status
        if 15 <= temperature <= 35:
            temp_status = "OPTIMAL"
            temp_color = "🟢"
        elif 35 < temperature <= 50:
            temp_status = "WARNING"
            temp_color = "🟡"
        else:
            temp_status = "CRITICAL"
            temp_color = "🔴"
        
        st.markdown("---")
        st.subheader("📋 Preview")
        
        col8, col9 = st.columns(2)
        with col8:
            st.metric("Health Status", f"{status_color} {health_status}")
        with col9:
            st.metric("Temperature Status", f"{temp_color} {temp_status}")
        
        # Submit button
        submitted = st.form_submit_button(
            "✅ Save Battery Record",
            use_container_width=True
        )
    
    if submitted:
        # Generate passport ID
        passport_id = f"EV-BATT-{datetime.now().strftime('%Y%m%d%H%M%S')}-UI"
        
        # Create record
        record = {
            'passport_id': passport_id,
            'manufacturer': manufacturer,
            'battery_type': battery_type,
            'capacity_kwh': round(capacity_kwh, 2),
            'production_date': prod_date.strftime('%Y-%m-%d'),
            'soh': round(soh, 2),
            'soc': round(soc, 2),
            'total_cycles': total_cycles,
            'temperature_celsius': round(temperature, 2),
            'health_status': health_status,
            'temperature_status': temp_status,
            'degradation_per_cycle': round(degradation_per_cycle, 4),
            'timestamp': datetime.now().isoformat(),
            'data_source': 'streamlit_ui',
            'user_wallet': st.session_state.get("user_wallet", "manual_entry")
        }
        
        # Validate
        is_valid, errors = data_loader.validate_battery_record(record)
        
        if is_valid:
            # Save to file
            data_file = Path("data/processed/user_entered_batteries.json")
            data_file.parent.mkdir(parents=True, exist_ok=True)
            
            existing_data = []
            if data_file.exists():
                with open(data_file, 'r') as f:
                    existing_data = json.load(f)
            
            existing_data.append(record)
            
            with open(data_file, 'w') as f:
                json.dump(existing_data, f, indent=2)
            
            # Display success
            st.success(f"Battery data stored successfully. EV Passport ID: {passport_id}")
            
            # Display record details
            with st.expander("📋 Record Details", expanded=True):
                record_df = pd.DataFrame([record])
                st.dataframe(record_df, use_container_width=True)
            
            st.info("📱 QR Code will be generated in Battery Records page")
            
            # Try to get prediction
            try:
                st.subheader("🤖 AI Prediction")
                
                # Load models
                import joblib
                model_path = sorted(Path("models/trained").glob("demo_battery_health_model_*.pkl"))
                
                if model_path:
                    model = joblib.load(model_path[-1])
                    scaler = joblib.load(sorted(Path("models/scalers").glob("demo_health_scaler_*.pkl"))[-1])
                    
                    # Prepare features
                    features = [
                        total_cycles,
                        total_cycles ** 2,
                        temperature,
                        temperature ** 2,
                        capacity_kwh,
                        degradation_per_cycle,
                        soc
                    ]
                    
                    # Predict
                    features_scaled = scaler.transform([features])
                    predicted_soh = model.predict(features_scaled)[0]
                    
                    col_pred1, col_pred2 = st.columns(2)
                    with col_pred1:
                        st.metric("Predicted SoH", f"{predicted_soh:.2f}%")
                    with col_pred2:
                        error = abs(predicted_soh - soh)
                        st.metric("Prediction Error", f"{error:.2f}%")
                    
                    st.info(f"✨ Model Prediction: {predicted_soh:.2f}% SoH (vs Entered: {soh}%)")
            except Exception as e:
                st.warning(f"⚠️ Could not load model for prediction: {str(e)}")
        
        else:
            st.error("❌ Validation failed:")
            for error in errors:
                st.error(f"  - {error}")
    
    # Display stored records
    st.markdown("---")
    st.subheader("📚 Recently Added Batteries")
    
    data_file = Path("data/processed/user_entered_batteries.json")
    if data_file.exists():
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        if data:
            # Show latest 5
            latest = data[-5:] if len(data) > 5 else data
            df = pd.DataFrame(latest)
            
            # Reorder columns for better display
            display_cols = [
                'passport_id', 'manufacturer', 'battery_type', 'capacity_kwh',
                'soh', 'soc', 'total_cycles', 'temperature_celsius',
                'health_status', 'timestamp'
            ]
            
            available_cols = [col for col in display_cols if col in df.columns]
            df_display = df[available_cols]
            
            st.dataframe(df_display, use_container_width=True)
            st.info(f"📊 Total records in system: {len(data)}")
        else:
            st.info("ℹ️ No battery records added yet.")
    else:
        st.info("ℹ️ No battery records added yet. Create your first one above!")
