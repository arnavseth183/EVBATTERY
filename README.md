# EV Battery Passport System

## Overview

This project implements a comprehensive **EV Battery Passport System** where:

- **IoT/QR Integration** captures battery manufacturing, usage, and recycling data
- **AI Models** predict battery health (SoH %), State of Charge (SoC %), and lifecycle anomalies
- **Blockchain Ledger** stores immutable battery records with complete traceability
- **Streamlit Dashboard** provides real-time battery data access and analysis
- **Regulatory Compliance** ensures data meets Battery Passport standards and SEBI requirements

---

## Project Goals

✅ **Data Collection** - Capture battery manufacturing, usage, recycling data via IoT/QR/Manual input  
✅ **Structured Datasets** - Build datasets for battery parameters (SoH, SoC, cycles, temperature)  
✅ **ML Models** - Battery health prediction and anomaly detection  
✅ **Battery Passport System** - End-to-end digital identity for EV batteries  
✅ **Query-based Access** - Enable efficient retrieval of battery information  

---

## Architecture

Battery Data (IoT/QR/Manual) → Data Preprocessing → AI Model (Health Prediction) → Blockchain Ledger → UI Dashboard

**Data Pipeline:**
- Historical battery parameters ingestion
- Feature engineering (cycle counting, temperature trends, degradation patterns)
- ML Classification & Regression model
- Confidence scoring

**Blockchain Storage:**
- BatteryRegistry.sol (Battery metadata)
- HealthRecordLedger.sol (Health metrics & predictions)
- CycleTracker.sol (Usage tracking)
- RecyclingRegistry.sol (End-of-life tracking)

---

## Key Features

- Real-time battery health monitoring (SoH, SoC, cycles, temperature)
- Battery ID and QR code generation
- IoT data ingestion and validation
- AI-powered anomaly detection
- Immutable blockchain records for regulatory compliance
- End-to-end traceability (manufacturing → usage → recycling)
- Interactive dashboard for all stakeholders
- Data export in CSV/JSON formats

---

## Stakeholders

- **Vehicle Owners** - Monitor battery health and residual value
- **Manufacturers** - Verify production data and manage warranties
- **Recyclers** - Track battery condition and recycling requirements
- **Regulatory Bodies** - Access standardized battery data
- **Resellers** - Authenticate battery history for used vehicles

---

## How To Run

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Start Ganache (blockchain node):

   ```bash
   docker-compose up
   ```

3. Deploy smart contracts:

   ```bash
   python blockchain_protocol/deployment/deploy_protocol.py
   ```

4. Initialize battery data (optional):

   ```bash
   python scripts/seed_battery_data.py
   ```

5. Run Streamlit dashboard:

   ```bash
   streamlit run app.py
   ```

---

## Project Milestones

**Kick Off (Month 1)**
- ✅ Understand EV battery ecosystem
- ✅ Define battery data collection parameters
- ✅ Study Battery Passport standards

**Milestone 1 (Month 2)**
- ✅ Collect and preprocess battery datasets
- ✅ Design data pipeline architecture
- ✅ Develop data ingestion scripts

**Milestone 2 (Month 4)**
- ✅ Build ML models for battery health prediction
- ✅ Evaluate and tune models
- ✅ Develop prototype application

**Closure (Month 6)**
- ✅ Finalize optimized model
- ✅ Deploy with real-time data
- ✅ Generate performance reports

---

## Tech Stack

- **Backend:** Python, FastAPI
- **ML/Data:** scikit-learn, pandas, numpy, XGBoost
- **Blockchain:** Solidity, Hardhat, Web3.py
- **Database:** JSON/CSV (local), On-chain Ledger
- **Frontend:** Streamlit
- **IoT Integration:** Mock IoT sensors, QR code support

---

## Data Structure

### Battery Passport ID
```json
{
  "passport_id": "EV-BATT-20260711-12345",
  "manufacturer": "Tesla/BYD/LG",
  "production_date": "2024-01-15",
  "battery_type": "Li-ion NCA",
  "capacity_kwh": 75.0,
  "current_soh": 87.5,
  "current_soc": 65.0,
  "total_cycles": 520,
  "max_temperature": 42.3,
  "last_updated": "2026-07-11T10:30:00Z"
}
```

---

## Academic Contribution

This project demonstrates:
- ML-based predictive analytics for battery lifecycle
- Blockchain-based distributed ledger for supply chain transparency
- Regulatory compliance automation (Battery Passport standards)
- IoT integration with blockchain for immutable data recording

---

## Disclaimer

This is a simulation-based educational project for battery lifecycle management research.
Real battery data is simulated for demonstration purposes.