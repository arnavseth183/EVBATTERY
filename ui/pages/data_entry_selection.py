"""
Data Entry Selection Page
Allows users to choose between manual data entry or automatic generation
"""

import streamlit as st
from datetime import datetime


def render_data_entry_selection():
    """Render the data entry selection page"""
    
    st.title("🔋 EV Battery Passport - Data Entry")
    st.markdown("### Choose how you want to add battery data")
    
    st.markdown("---")
    
    # Create two main options
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📝 Manual Data Entry
        
        Enter battery data manually through our comprehensive form.
        
        **Features:**
        - Detailed battery specifications
        - Real-time health status calculation
        - AI-powered health predictions
        - QR code generation
        """)
        
        if st.button("📝 Enter Data Manually", use_container_width=True, key="manual_entry"):
            st.session_state.data_entry_mode = "manual"
            st.rerun()
    
    with col2:
        st.markdown("""
        ### 🤖 Automatic Generation
        
        Generate sample battery data for testing and demonstration.
        
        **Features:**
        - Random battery specifications
        - Simulated health data
        - Quick testing capabilities
        - Multiple battery generation
        """)
        
        if st.button("🤖 Generate Automatically", use_container_width=True, key="auto_entry"):
            st.session_state.data_entry_mode = "automatic"
            st.rerun()
    
    st.markdown("---")
    
    # Information section
    st.info("""
    💡 **Recommendation:** Use manual entry for real battery data and automatic generation for testing/demo purposes.
    
    Both options will:
    - Generate a unique Battery Passport ID
    - Create QR codes for tracking
    - Store data securely
    - Enable blockchain registration
    """)


def render_automatic_generation():
    """Render automatic battery data generation form"""
    
    st.title("🤖 Automatic Battery Data Generation")
    st.markdown("Generate sample battery data for testing")
    
    # Generation options
    col1, col2 = st.columns(2)
    
    with col1:
        num_batteries = st.number_input(
            "Number of batteries to generate",
            min_value=1,
            max_value=10,
            value=1,
            step=1
        )
    
    with col2:
        battery_type = st.selectbox(
            "Battery Type",
            ["Li-ion NCA", "Li-ion NCM", "Li-ion LFP", "Li-poly", "Solid-State", "Random"]
        )
    
    # Generate button
    if st.button("🚀 Generate Batteries", use_container_width=True):
        import json
        import random
        from pathlib import Path
        
        generated_batteries = []
        
        for i in range(num_batteries):
            # Random battery data
            manufacturers = ["Tesla", "BYD", "LG", "Panasonic", "Samsung", "CATL"]
            selected_type = battery_type if battery_type != "Random" else random.choice(["Li-ion NCA", "Li-ion NCM", "Li-ion LFP"])
            
            cycles = random.randint(100, 2000)
            base_soh = max(60, 100 - (cycles * 0.015))
            soh = round(base_soh + random.uniform(-5, 5), 2)
            soh = max(0, min(100, soh))
            
            battery_data = {
                "passport_id": f"EV-BATT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{i:04d}",
                "manufacturer": random.choice(manufacturers),
                "battery_type": selected_type,
                "capacity_kwh": round(random.uniform(50, 150), 2),
                "production_date": datetime.now().strftime('%Y-%m-%d'),
                "soh": soh,
                "soc": round(random.uniform(20, 90), 2),
                "total_cycles": cycles,
                "temperature_celsius": round(random.uniform(15, 45), 2),
                "health_status": "GOOD" if soh >= 80 else "FAIR" if soh >= 70 else "DEGRADED",
                "temperature_status": "OPTIMAL",
                "degradation_per_cycle": round((100 - soh) / max(cycles, 1), 4),
                "data_source": "automatic_generation",
                "user_wallet": st.session_state.get("user_wallet", "system"),
                "timestamp": datetime.now().isoformat()
            }
            
            generated_batteries.append(battery_data)
        
        # Save to file
        data_file = Path("data/processed/auto_generated_batteries.json")
        data_file.parent.mkdir(parents=True, exist_ok=True)
        
        existing_data = []
        if data_file.exists():
            with open(data_file, 'r') as f:
                existing_data = json.load(f)
        
        existing_data.extend(generated_batteries)
        
        with open(data_file, 'w') as f:
            json.dump(existing_data, f, indent=2)
        
        st.success(f"Battery data stored successfully. Generated {num_batteries} battery records.")
        
        # Display generated data
        import pandas as pd
        df = pd.DataFrame(generated_batteries)
        st.dataframe(df, use_container_width=True)
        
        # Option to add to passport system
        if st.button("➕ Add to Battery Passport System", use_container_width=True):
            # This would integrate with the battery passport controller
            st.info("Batteries will be added to passport system with QR codes")
    
    # Back button
    if st.button("← Back to Selection", use_container_width=True):
        if "data_entry_mode" in st.session_state:
            del st.session_state.data_entry_mode
        st.rerun()
