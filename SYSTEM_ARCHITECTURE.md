# EV Battery Passport System - Architecture & Data Flow

## 🏗️ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    EV BATTERY PASSPORT SYSTEM                           │
│                        (6-Month Project)                                 │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  TIER 1: DATA INGESTION LAYER                                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐               │
│  │ IoT Sensors  │   │ QR Code      │   │ Manual       │               │
│  │ (MQTT)       │   │ Reader       │   │ Input (UI)   │               │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘               │
│         │                  │                  │                        │
│         └──────────────────┴──────────────────┘                        │
│                          │                                             │
│              scripts/battery_data_loader.py ◄── Ingestion             │
│                          │                                             │
│         ┌────────────────┴────────────────┐                           │
│         ▼                                 ▼                           │
│    CSV Input            JSON Input                                   │
│    (Raw Data)           (Raw Data)                                   │
│         │                    │                                        │
└─────────┼────────────────────┼──────────────────────────────────────┘
          │                    │
┌─────────┴────────────────────┴──────────────────────────────────────┐
│  TIER 2: DATA VALIDATION & PREPROCESSING                             │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ battery_data_loader.py                                      │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │                                                             │   │
│  │  1. Schema Validation                                      │   │
│  │     ├─ Required fields: passport_id, soh, soc, temp, etc   │   │
│  │     └─ Range checks: SoH(0-100%), Temp(15-60°C)            │   │
│  │                                                             │   │
│  │  2. Data Cleaning                                          │   │
│  │     ├─ Remove duplicates                                   │   │
│  │     ├─ Handle missing values                               │   │
│  │     └─ Normalize ranges                                    │   │
│  │                                                             │   │
│  │  3. Feature Engineering                                    │   │
│  │     ├─ Degradation rate: (100 - SoH) / cycles             │   │
│  │     ├─ Temperature volatility                              │   │
│  │     ├─ Cycle efficiency                                    │   │
│  │     └─ Age patterns                                        │   │
│  │                                                             │   │
│  │  4. Health Classification                                  │   │
│  │     ├─ EXCELLENT: 90-100%   ├─ DEGRADED: 60-70%           │   │
│  │     ├─ GOOD: 80-90%         └─ POOR: <60%                 │   │
│  │     └─ FAIR: 70-80%                                        │   │
│  │                                                             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│         │                                                            │
│         ▼                                                            │
│    ✓ Validated                                                      │
│    ✓ Cleaned                                                        │
│    ✓ Features Engineered                                           │
│                                                                     │
└─────────────┬───────────────────────────────────────────────────────┘
              │
     ┌────────┴────────┐
     ▼                 ▼
CSV/JSON Output   data/processed/
(Processed Data)  (Storage)

┌──────────────────────────────────────────────────────────────────────┐
│  TIER 3: MACHINE LEARNING MODELS                                     │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ai_oracle/training/battery_health_trainer.py                       │
│                                                                      │
│  ┌────────────────────────┐     ┌────────────────────────┐         │
│  │  SoH PREDICTION MODEL  │     │ ANOMALY DETECTION      │         │
│  ├────────────────────────┤     ├────────────────────────┤         │
│  │                        │     │                        │         │
│  │ Input Features:        │     │ Input Features:        │         │
│  │ • Total Cycles        │     │ • Cycle Count         │         │
│  │ • Temperature         │     │ • Temperature         │         │
│  │ • Capacity            │     │ • Degradation Rate    │         │
│  │ • Degradation Rate    │     │ • SoC                 │         │
│  │ • SoC                 │     │                        │         │
│  │                        │     │ Algorithm:            │         │
│  │ Algorithm:            │     │ Isolation Forest      │         │
│  │ RandomForest          │     │                        │         │
│  │ (100 trees)           │     │ Output:               │         │
│  │                        │     │ Anomaly Score (0-1)   │         │
│  │ Output:               │     │ Prediction: Normal/-1 │         │
│  │ Predicted SoH (%)     │     │                        │         │
│  │ Confidence Score      │     │ Performance:          │         │
│  │                        │     │ Precision: >90%       │         │
│  │ Performance:          │     │ Contamination: 10%    │         │
│  │ R² Score: >0.85       │     │                        │         │
│  │ MAE: <3%              │     │                        │         │
│  └────────────────────────┘     └────────────────────────┘         │
│         │                               │                           │
│         └───────────┬───────────────────┘                           │
│                     ▼                                               │
│          models/trained/                                           │
│          • battery_health_model.pkl                               │
│          • anomaly_model.pkl                                      │
│                                                                    │
│          models/scalers/                                          │
│          • health_scaler.pkl                                      │
│          • anomaly_scaler.pkl                                     │
│                                                                    │
└────────────┬─────────────────────────────────────────────────────┘
             │
             ▼ (Loaded by app.py)
        
┌──────────────────────────────────────────────────────────────────────┐
│  TIER 4: BLOCKCHAIN LAYER (Smart Contracts)                          │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────────┐  ┌────────────────────────┐            │
│  │ BATTERY REGISTRY      │  │ HEALTH RECORD LEDGER  │            │
│  ├────────────────────────┤  ├────────────────────────┤            │
│  │                        │  │                        │            │
│  │ Function:             │  │ Function:             │            │
│  │ registerBattery()     │  │ recordHealth()        │            │
│  │                        │  │                        │            │
│  │ Data:                 │  │ Data:                 │            │
│  │ • Passport ID         │  │ • Passport ID         │            │
│  │ • Manufacturer        │  │ • SoH, SoC            │            │
│  │ • Battery Type        │  │ • Temperature         │            │
│  │ • Capacity            │  │ • Cycles              │            │
│  │ • Owner Address       │  │ • Timestamp           │            │
│  │ • Production Date     │  │ • AI Prediction       │            │
│  │                        │  │ • Anomaly Score       │            │
│  └────────────────────────┘  └────────────────────────┘            │
│         │                            │                             │
│  ┌──────┴────────────────────────────┴─────────┐                  │
│  │                                               │                 │
│  ├───────────────────────────────────────────────┤                 │
│  │ CYCLE TRACKER       │  RECYCLING REGISTRY    │                 │
│  ├───────────────────────────────────────────────┤                 │
│  │                     │                         │                 │
│  │ recordCycle()       │ markForRecycling()      │                 │
│  │                     │                         │                 │
│  │ Data:               │ Data:                   │                 │
│  │ • Cycle #           │ • Passport ID           │                 │
│  │ • Depth             │ • Recycler Address      │                 │
│  │ • Efficiency        │ • Condition             │                 │
│  │                     │ • Date                  │                 │
│  │                     │                         │                 │
│  └────────┬──────────────────┬──────────────────┘                 │
│           │                  │                                    │
│           └──────────┬───────┘                                    │
│                      ▼                                            │
│         Hardhat Node (http://localhost:8545)                     │
│         ├─ 10 pre-funded accounts                               │
│         ├─ Local blockchain simulation                          │
│         └─ Instant tx confirmation                             │
│                                                                 │
└─────────────┬──────────────────────────────────────────────────┘
              │
┌─────────────┴──────────────────────────────────────────────────────┐
│  TIER 5: USER INTERFACE & DASHBOARD (Streamlit)                    │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  app.py (Main Entry Point)                                        │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ 🔐 LOGIN/AUTHENTICATION                                 │    │
│  │ ├─ Create Account     (wallet_generator.py)            │    │
│  │ ├─ Login with Password (user_wallet_registry.py)       │    │
│  │ └─ Recover Account    (private key recovery)           │    │
│  └──────────────────────────────────────────────────────────┘    │
│         │ (After login)                                          │
│         ▼                                                         │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ NAVIGATION SIDEBAR - 5 Main Pages                       │    │
│  ├──────────────────────────────────────────────────────────┤    │
│  │                                                          │    │
│  │  📊 DASHBOARD                                           │    │
│  │    ├─ Overview of all batteries                        │    │
│  │    ├─ Key metrics (Total batteries, Avg Health)        │    │
│  │    └─ Recent activity                                  │    │
│  │                                                          │    │
│  │  🔋 BATTERY RECORDS                                    │    │
│  │    ├─ Add new battery                                  │    │
│  │    ├─ Search battery by passport ID                    │    │
│  │    ├─ View battery details                             │    │
│  │    ├─ Edit battery information                         │    │
│  │    └─ Generate QR code                                 │    │
│  │                                                          │    │
│  │  📈 HEALTH ANALYTICS                                   │    │
│  │    ├─ SoH trend analysis                               │    │
│  │    ├─ Temperature trends                               │    │
│  │    ├─ Cycle predictions                                │    │
│  │    ├─ Anomaly alerts                                   │    │
│  │    └─ Export reports (CSV/JSON/PDF)                    │    │
│  │                                                          │    │
│  │  ⛓️  BLOCKCHAIN EXPLORER                               │    │
│  │    ├─ View transaction history                         │    │
│  │    ├─ Verify on-chain records                          │    │
│  │    ├─ Track lifecycle events                           │    │
│  │    └─ Audit trail                                      │    │
│  │                                                          │    │
│  │  ⚙️  SETTINGS                                          │    │
│  │    ├─ User profile                                     │    │
│  │    ├─ System configuration                             │    │
│  │    ├─ Data export                                      │    │
│  │    └─ Logout                                           │    │
│  │                                                          │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Flow Diagrams

### **Flow 1: Add Battery (Store Passport)**

```
User Input (UI)
    │
    ├─ Passport ID
    ├─ Manufacturer
    ├─ Battery Type
    ├─ Capacity
    ├─ SoH, SoC
    ├─ Cycles
    ├─ Temperature
    └─ Production Date
    │
    ▼
app.py (Collect Input)
    │
    ▼
battery_data_loader.py (Validate)
    ├─ Check required fields
    ├─ Validate ranges
    └─ Generate health status
    │
    ▼
blockchain_protocol/
execution_engine/protocol_controller.py
    │
    ▼
contracts/BatteryRegistry.sol
    ├─ registerBattery()
    └─ Store on blockchain
    │
    ▼
blockchain (Hardhat Node)
    │
    ▼
UI Display
    ├─ Confirmation message
    ├─ Passport ID
    └─ QR Code generated
```

### **Flow 2: Query Battery Health**

```
User Search (UI)
    │
    ├─ Passport ID
    │
    ▼
app.py (Get Input)
    │
    ▼
blockchain_protocol/
execution_engine/protocol_controller.py
    │
    ├─ Query BatteryRegistry.sol
    ├─ Fetch HealthRecordLedger.sol
    └─ Get latest health record
    │
    ▼
ai_oracle/prediction/predictor.py
    │
    ├─ Load battery_health_model.pkl
    ├─ Load health_scaler.pkl
    └─ Predict next SoH degradation
    │
    ▼
UI Display
    ├─ Current SoH: 87%
    ├─ Current SoC: 65%
    ├─ Total Cycles: 520
    ├─ Temperature: 28.3°C
    ├─ Health Status: GOOD
    ├─ Predicted SoH (30 days): 85%
    ├─ Anomaly Status: NORMAL
    └─ Recommendations
```

### **Flow 3: Anomaly Detection**

```
Battery Data (Real-time)
    │
    ├─ SoH, SoC, Cycles
    ├─ Temperature
    └─ Degradation rate
    │
    ▼
anomaly_model.pkl (Isolation Forest)
    │
    ├─ Feature scaling (anomaly_scaler.pkl)
    └─ Detect outliers
    │
    ▼
Anomaly Score
    │
    ├─ Score < -0.5: ANOMALY DETECTED 🚨
    └─ Score >= -0.5: NORMAL ✓
    │
    ▼
UI Alert
    ├─ Display anomaly warnings
    ├─ Recommend maintenance
    └─ Notify relevant parties
```

---

## 💾 Data Storage Architecture

```
data/
├── battery_data/              (Raw Input)
│   ├── sample_data.csv
│   ├── sample_data.json
│   └── iot_sensor_dumps/
│
├── processed/                 (Cleaned & Engineered)
│   ├── battery_data_processed.csv
│   ├── battery_data_processed.json
│   ├── battery_report_*.json
│   └── statistics.json
│
└── backup/                    (Backups)
    └── daily_backups/

models/
├── trained/                   (ML Models)
│   ├── battery_health_model.pkl
│   ├── anomaly_model.pkl
│   └── training_history.pkl
│
└── scalers/                   (Feature Scalers)
    ├── health_scaler.pkl
    └── anomaly_scaler.pkl

blockchain/
└── contracts_deployed/
    └── addresses.json         (Contract addresses)

logs/
├── app.log                    (General events)
├── battery_health.log         (ML events)
├── blockchain.log             (Smart contract events)
└── data_ingestion.log         (Data pipeline events)
```

---

## 🔗 Module Dependencies

```
app.py (Main)
├─ config.py
├─ battery_data_loader.py
├─ battery_health_trainer.py (Predictor)
├─ blockchain_protocol/
│  ├─ execution_engine/protocol_controller.py
│  ├─ web3_layer/web3_provider.py
│  └─ storage/user_wallet_registry.py
└─ ui/
   ├─ pages/dashboard.py
   ├─ pages/battery_records.py
   └─ pages/health_analytics.py
```

---

## 📈 Model Training Pipeline

```
Input Data
    │
    ▼
Feature Preparation
    ├─ Select features: [cycles, temp, capacity, degradation_rate]
    ├─ Handle missing values
    └─ Split train/test (80/20)
    │
    ▼
Model 1: SoH Prediction (RandomForest)
    ├─ Fit on training data
    ├─ Predict on test data
    ├─ Evaluate: MAE, MSE, R²
    └─ Cross-validate (5-fold)
    │
    ▼
Model 2: Anomaly Detection (Isolation Forest)
    ├─ Fit on all data
    ├─ Compute anomaly scores
    ├─ Predict: Normal (1) or Anomaly (-1)
    └─ Evaluate: Contamination rate
    │
    ▼
Save Models
    ├─ pickle models
    ├─ Save scalers
    └─ Log metrics
    │
    ▼
Ready for Predictions
```

---

## 🎯 End-to-End Process

```
Month 1: Setup & Configuration ✅
├─ Define battery parameters
├─ Configure config.py
└─ Create documentation

Month 2: Data Pipeline 🔄
├─ Generate synthetic data (100 batteries)
├─ Validate & preprocess
└─ Feature engineering

Month 3: Blockchain Setup
├─ Deploy smart contracts
├─ Test on-chain recording
└─ Verify immutability

Month 4: ML Models
├─ Train SoH prediction (Target >85% accuracy)
├─ Train anomaly detection
└─ Evaluate & optimize

Month 5: UI Integration
├─ Create battery management pages
├─ Integrate ML predictions
├─ Add blockchain queries
└─ Testing

Month 6: Deployment & Closure
├─ End-to-end system test
├─ Performance verification
├─ Generate reports
└─ Project completion
```

---

**Status:** ✅ Architecture Designed and Ready for Implementation  
**Date:** 2026-07-11
