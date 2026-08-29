import streamlit as st
from datetime import datetime
import plotly.graph_objects as go
import pandas as pd


def render_dashboard(predictor, protocol, battery_health, selected_battery, data_mode, current_user=None):

    st.title("🔋 EV Battery Passport Dashboard")
    st.markdown("Real-time battery health monitoring with AI predictions")
    
    # Store current_user in session for audit purposes
    if current_user:
        st.session_state.current_user = current_user

    col1, col2, col3, col4, col5 = st.columns(5)

    # ----------------------------
    # BATTERY HEALTH DATA
    # ----------------------------
    
    soh = battery_health.get("soh", 0.0)
    soc = battery_health.get("soc", 0.0)
    temperature = battery_health.get("temperature", 0.0)
    health_status = battery_health.get("health_status", "UNKNOWN")
    confidence = battery_health.get("confidence", 0.0)
    total_cycles = battery_health.get("total_cycles", 0)
    capacity_kwh = battery_health.get("capacity_kwh", 0.0)
    manufacturer = battery_health.get("manufacturer", "Unknown")
    battery_type = battery_health.get("battery_type", "Unknown")
    passport_id = battery_health.get("passport_id", selected_battery)

    # ----------------------------
    # METRICS
    # ----------------------------
    with col1:
        st.metric("State of Health (SoH)", f"{soh:.1f}%")

    with col2:
        st.metric("State of Charge (SoC)", f"{soc:.1f}%")

    with col3:
        st.metric("Temperature", f"{temperature:.1f}°C")

    with col4:
        st.metric("Cycles", f"{total_cycles}")

    with col5:
        st.metric("Capacity", f"{capacity_kwh:.1f} kWh")

    # ----------------------------
    # BATTERY HEALTH GAUGE CHART
    # ----------------------------
    st.subheader("Battery Health Gauges")

    col_left, col_right = st.columns(2)

    # SoH Gauge
    with col_left:
        fig_soh = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=soh,
            title={'text': "State of Health (%)"},
            delta={'reference': 90, 'prefix': "vs target: "},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 60], 'color': "lightgray"},
                    {'range': [60, 70], 'color': "orange"},
                    {'range': [70, 80], 'color': "yellow"},
                    {'range': [80, 90], 'color': "lightgreen"},
                    {'range': [90, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 80
                }
            }
        ))
        fig_soh.update_layout(height=350)
        st.plotly_chart(fig_soh, use_container_width=True)

    # Temperature Gauge
    with col_right:
        temp_color = "green" if 15 <= temperature <= 35 else "orange" if temperature <= 50 else "red"
        fig_temp = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=temperature,
            title={'text': "Temperature (°C)"},
            delta={'reference': 25, 'prefix': "vs optimal: "},
            gauge={
                'axis': {'range': [0, 80]},
                'bar': {'color': temp_color},
                'steps': [
                    {'range': [0, 15], 'color': "lightblue"},
                    {'range': [15, 35], 'color': "lightgreen"},
                    {'range': [35, 50], 'color': "yellow"},
                    {'range': [50, 80], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "darkred", 'width': 4},
                    'thickness': 0.75,
                    'value': 60
                }
            }
        ))
        fig_temp.update_layout(height=350)
        st.plotly_chart(fig_temp, use_container_width=True)

    st.markdown("---")

    # ----------------------------
    # BATTERY STATUS CARD
    # ----------------------------
    st.subheader("Battery Status Summary")

    status_color = {
        "EXCELLENT": "🟢",
        "GOOD": "🟢", 
        "FAIR": "🟡",
        "DEGRADED": "🟠",
        "POOR": "🔴",
        "UNKNOWN": "⚪"
    }

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.info(f"**Status:** {status_color.get(health_status, '⚪')} {health_status}")
    
    with col2:
        st.warning(f"**Manufacturer:** {manufacturer}")
    
    with col3:
        st.success(f"**Type:** {battery_type}")
    
    with col4:
        st.info(f"**Passport ID:** {passport_id[-12:]}")

    # ----------------------------
    # ADDITIONAL BATTERY INFORMATION
    # ----------------------------
    st.subheader("Battery Details")
    
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.markdown(f"**Manufacturer:** {manufacturer}")
        st.markdown(f"**Battery Type:** {battery_type}")
        st.markdown(f"**Passport ID:** {passport_id}")
    
    with col_info2:
        st.markdown(f"**Health Status:** {health_status}")
        st.markdown(f"**Temperature Status:** {battery_health.get('temperature_status', 'UNKNOWN')}")
        if total_cycles > 0:
            degradation = (100 - soh) / total_cycles
            st.markdown(f"**Degradation Rate:** {degradation:.4f}% per cycle")

    # ----------------------------
    # AI PREDICTION SECTION
    # ----------------------------
    st.subheader("🤖 AI Future Health Prediction")
    
    try:
        # Use the battery health predictor
        prediction = predictor.predict_battery_health(battery_health)
        
        # Check if prediction has the expected keys
        if 'predicted_future_soh' in prediction:
            col_pred1, col_pred2, col_pred3 = st.columns(3)
            
            with col_pred1:
                st.metric("Current SoH", f"{prediction['current_soh']:.1f}%")
            
            with col_pred2:
                st.metric("Predicted SoH (after {prediction['future_cycles']} cycles)", f"{prediction['predicted_future_soh']:.1f}%")
            
            with col_pred3:
                st.metric("Expected Degradation", f"{prediction['degradation_prediction']:.1f}%")
            
            st.metric("Prediction Confidence", f"{prediction['confidence']:.0%}")
        else:
            # Fallback for old prediction format
            st.warning("Using fallback prediction format")
            col_pred1, col_pred2 = st.columns(2)
            with col_pred1:
                st.metric("Current SoH", f"{soh:.1f}%")
            with col_pred2:
                st.metric("Predicted Future SoH", f"{max(0, soh - 1.5):.1f}% (after 100 cycles)")
        
        # Health query response in problem statement format
        st.info(f"Battery SoH is {soh:.1f}%, cycles: {total_cycles}.")
        
        # Anomaly detection
        anomaly_result = predictor.predict_anomaly(battery_health)
        if anomaly_result['has_anomaly']:
            st.error(f"⚠️ {anomaly_result['anomaly_count']} Anomalies Detected:")
            for anomaly in anomaly_result['anomalies']:
                st.warning(f"  - {anomaly['type']}: {anomaly['value']} (Threshold: {anomaly['threshold']})")
        else:
            st.success("✅ No anomalies detected")
            
    except Exception as e:
        st.warning(f"AI prediction unavailable: {e}")
        # Show basic health info even if prediction fails
        st.info(f"Battery SoH is {soh:.1f}%, cycles: {total_cycles}.")

    # ----------------------------
    # TIMESTAMP
    # ----------------------------
    st.write("Last Updated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    st.markdown("---")
    st.caption("EV Battery Passport System - Real-time battery monitoring and health predictions.")