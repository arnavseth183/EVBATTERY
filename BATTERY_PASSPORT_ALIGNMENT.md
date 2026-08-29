# EV Battery Passport System - Alignment Guide

**Date:** 2026-07-11  
**Status:** ✅ Core Alignment Complete  
**Project Duration:** 6 Months  
**Team Size:** 3 Students

---

## 📋 Executive Summary

This document outlines how the codebase has been transformed from a **Decentralized Trading Platform** to an **EV Battery Passport System** with end-to-end capability for battery lifecycle tracking, health prediction, and regulatory compliance.

---

## 🎯 Project Milestones & Goals

### **Kick Off (Month 1)**
- ✅ Understand EV battery ecosystem and requirements
- ✅ Define battery data collection parameters (SoH, SoC, cycles, temperature)
- ✅ Study Battery Passport standards
- 📌 **Status:** Configuration files updated

### **Milestone 1 (Month 2)**
- 🔄 Collect and preprocess battery datasets
- 🔄 Design data pipeline architecture (IoT/QR → Processing → Storage)
- 🔄 Develop data ingestion scripts
- 📌 **Task:** Create `scripts/battery_data_loader.py`

### **Milestone 2 (Month 4)**
- 🔄 Build ML models for battery health prediction
- 🔄 Develop anomaly detection model
- 🔄 Create prototype application with battery passport UI
- 📌 **Task:** Update `ai_oracle/training/` for battery health models

### **Closure (Month 6)**
- ⏳ Finalize optimized model and system integration
- ⏳ Deploy with real-time data ingestion
- ⏳ Generate performance reports
- ⏳ Compare with existing Battery Passport approaches

---

## 📁 Files Modified & Aligned

### **1. 📄 README.md** ✅ COMPLETE
**Changes Made:**
- ✅ Changed title from "Decentralized AI Blockchain Trading" → "EV Battery Passport System"
- ✅ Updated overview to focus on battery lifecycle management
- ✅ Added stakeholder information (Vehicle Owners, Manufacturers, Recyclers, Regulators)
- ✅ Updated data structure example with battery passport fields (passport_id, SoH, SoC, cycles, temperature)
- ✅ Added Battery Passport specific features and tech stack
- ✅ Updated project milestones and goals

**Key Sections:**
```markdown
- Project Goals: Data Collection → Structured Datasets → ML Models → Battery Passport System
- Architecture: Battery Data → Preprocessing → AI Model → Blockchain → Dashboard
- Features: Real-time monitoring, QR code generation, IoT integration, anomaly detection
- Stakeholders: Owners, Manufacturers, Recyclers, Regulators, Resellers
```

---

### **2. 📊 CODEBASE_OVERVIEW.md** ✅ PARTIAL
**Changes Made:**
- ✅ Updated Project Name & Purpose (header section)
- ✅ Renamed from "DAPPTRADE" to "EV Battery Passport System"
- ⏳ **PENDING:** Full module documentation update

**Sections to Review/Update:**
- [ ] Section 2.1: AI Oracle Layer (battery health vs. trading signals)
- [ ] Section 2.2: Smart Contracts (BatteryRegistry vs. TradingProtocol)
- [ ] Section 2.4: Data structures (battery data vs. trade data)

---

### **3. ⚙️ config.py** ✅ COMPLETE
**Changes Made:**
- ✅ `APP_NAME`: "Decentralized AI Blockchain Trading" → "EV Battery Passport System"
- ✅ Replaced SUPPORTED_STOCKS → BATTERY_TYPES (Li-ion NCA, NCM, LFP, etc.)
- ✅ Added BATTERY_HEALTH_THRESHOLDS (EXCELLENT 90-100%, GOOD 80-90%, etc.)
- ✅ Added TEMPERATURE_THRESHOLDS (OPTIMAL_MIN 15°C, CRITICAL_MAX 60°C)
- ✅ Replaced MODEL_PATH → BATTERY_HEALTH_MODEL_PATH & BATTERY_ANOMALY_MODEL_PATH
- ✅ Added IoT settings (IOT_ENABLED, QR_CODE_ENABLED, MQTT configuration)
- ✅ Added BATTERY_DATA_DIR and PROCESSED_DATA_DIR
- ✅ Updated logging paths (battery_health.log, data_ingestion.log)
- ✅ Added REGULATORY_COMPLIANCE_MODE = "BATTERY_PASSPORT_2030"

**Battery-Specific Parameters:**
```python
BATTERY_HEALTH_THRESHOLDS = {
    "EXCELLENT": (90, 100),
    "GOOD": (80, 90),
    "FAIR": (70, 80),
    "DEGRADED": (60, 70),
    "POOR": (0, 60)
}

TEMPERATURE_THRESHOLDS = {
    "OPTIMAL_MIN": 15,
    "OPTIMAL_MAX": 35,
    "WARNING_MAX": 50,
    "CRITICAL_MAX": 60
}
```

---

### **4. 🚀 app.py** ✅ COMPLETE
**Changes Made:**
- ✅ Updated `page_title`: "Decentralized AI Blockchain Trading" → "EV Battery Passport System"
- ✅ Replaced trade panel & risk dashboard → battery records & health analytics pages
- ✅ Updated login message: "Blockchain Trading Login" → "EV Battery Passport - Access"
- ✅ Changed sidebar navigation from trading modules to battery management modules
- ✅ Updated UI labels and descriptions for battery passport context
- ✅ Modified session state variables (last_auto_trade → last_data_sync)
- ✅ Updated quick stats to show battery metrics (Batteries, Avg Health %)

**New Navigation Pages:**
```
📊 Dashboard
🔋 Battery Records
📈 Health Analytics
⛓️ Blockchain Explorer
⚙️ Settings
```

**Removed Trading Elements:**
- ❌ Trade Panel
- ❌ Risk Dashboard
- ❌ Governance voting
- ❌ Portfolio positions

---

### **5. 📦 requirements.txt** ✅ COMPLETE
**Changes Made:**
- ✅ Added IoT dependencies: `paho-mqtt` (MQTT protocol)
- ✅ Added QR code support: `qrcode[pil]`, `pillow`
- ✅ Reorganized into logical sections (Blockchain, Web Framework, Database, ML, etc.)
- ✅ Added data export: `openpyxl`, `xlsxwriter`
- ✅ Maintained core ML libraries (scikit-learn, XGBoost, LightGBM)
- ✅ Kept web3 stack for blockchain integration

**New Battery-Specific Dependencies:**
```
paho-mqtt           # MQTT for IoT sensors
qrcode[pil]         # QR code generation
pillow              # Image processing
openpyxl            # Excel export
xlsxwriter          # XLS export
```

---

## 🔄 Required Updates (Next Steps)

### **Phase 1: Data Layer** (Month 2)

#### **1. Battery Data Loader Script** 📝
**File:** `scripts/battery_data_loader.py`
**Purpose:** Ingest battery data from IoT/QR/Manual sources
**Functionality:**
```python
- Parse CSV/JSON battery datasets
- Validate battery parameters (SoH, SoC, cycles, temperature)
- Check against TEMPERATURE_THRESHOLDS
- Format for ML pipeline
- Store in data/processed/
```

**Required Parameters:**
```json
{
  "passport_id": "EV-BATT-20260711-12345",
  "manufacturer": "Tesla/BYD/LG",
  "battery_type": "Li-ion NCM",
  "capacity_kwh": 75.0,
  "soh": 87.5,
  "soc": 65.0,
  "total_cycles": 520,
  "temperature": 28.5,
  "timestamp": "2026-07-11T10:30:00Z"
}
```

#### **2. Battery Dataset Creation** 📊
**File:** `data/battery_data/sample_battery_data.csv`
**Contents:** 100+ battery records with synthetic data
**Columns:** passport_id, manufacturer, battery_type, capacity, SoH, SoC, cycles, temperature, health_status

---

### **Phase 2: ML Models** (Month 4)

#### **1. Battery Health Prediction Model** 🧠
**File:** `ai_oracle/training/battery_health_trainer.py`
**Type:** Regression model for SoH prediction
**Features:**
- Cycle count
- Temperature history (max, min, avg)
- Usage patterns
- Time since manufacture

**Target:** Predict next-period SoH degradation

#### **2. Anomaly Detection Model** 🚨
**File:** `ai_oracle/training/anomaly_trainer.py`
**Type:** Isolation Forest / One-Class SVM
**Purpose:** Detect abnormal battery behavior
- Temperature spikes
- Abnormal cycle rates
- Rapid capacity loss

#### **3. Feature Engineering for Batteries** ⚙️
**File:** `ai_oracle/feature_engineering/battery_features.py`
**Features to Engineer:**
- Degradation rate (SoH decline per cycle)
- Temperature volatility
- Cycle efficiency (capacity retention)
- Aging patterns

---

### **Phase 3: Smart Contracts** (Month 4-5)

#### **Smart Contracts to Create/Rename:**

| Current Contract | New Purpose | New Name |
|-----------------|------------|----------|
| TradingProtocol.sol | Battery data recording | BatteryRegistry.sol |
| Ledger.sol | Health metrics history | HealthRecordLedger.sol |
| (New) | Cycle tracking | CycleTracker.sol |
| (New) | Recycling info | RecyclingRegistry.sol |
| RiskManager.sol | Battery status alerts | HealthAlertManager.sol |

**Key Contract Functions:**
```solidity
// BatteryRegistry.sol
function registerBattery(string passportId, string manufacturer, uint capacity) → registered

// HealthRecordLedger.sol
function recordHealth(string passportId, uint soh, uint soc, uint temp) → recorded

// CycleTracker.sol
function recordCycle(string passportId, uint cycleNumber) → recorded

// RecyclingRegistry.sol
function markForRecycling(string passportId, string recyclerAddress) → marked
```

---

### **Phase 4: UI Pages** (Month 4-5)

#### **New/Updated Pages:**

| Page | Purpose | Location |
|------|---------|----------|
| Dashboard | Overview of all batteries | `ui/pages/dashboard.py` |
| Battery Records | CRUD for battery passports | `ui/pages/battery_records.py` |
| Health Analytics | SoH trends, predictions | `ui/pages/health_analytics.py` |
| Blockchain Explorer | View on-chain records | `ui/pages/blockchain_explorer.py` |
| QR Code Generator | Generate battery QR codes | `ui/pages/qr_generator.py` |

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│         EV BATTERY PASSPORT SYSTEM ARCHITECTURE             │
└─────────────────────────────────────────────────────────────┘

1. DATA INGESTION LAYER
   ↓
   ├─ IoT Sensors (MQTT)
   │  └─ Temperature, SoC, cycle data real-time
   │
   ├─ QR Code Reader
   │  └─ Battery ID & basic metadata
   │
   └─ Manual Input
      └─ Manufacturer data, recycling info

2. DATA VALIDATION LAYER
   ↓
   ├─ Schema validation (required fields)
   ├─ Range checks (temperature bounds, SoH 0-100)
   └─ Data quality scoring

3. FEATURE ENGINEERING LAYER
   ↓
   ├─ Degradation rate calculation
   ├─ Temperature volatility
   ├─ Cycle efficiency metrics
   └─ Aging pattern extraction

4. AI PREDICTION LAYER
   ↓
   ├─ Battery Health Model (RandomForest Regression)
   │  └─ Output: Predicted SoH degradation
   │
   └─ Anomaly Detection Model (Isolation Forest)
      └─ Output: Anomaly score (0-1)

5. BLOCKCHAIN STORAGE LAYER
   ↓
   ├─ BatteryRegistry.sol - Battery metadata
   ├─ HealthRecordLedger.sol - Health metrics history
   ├─ CycleTracker.sol - Usage tracking
   └─ RecyclingRegistry.sol - End-of-life info

6. QUERY & REPORTING LAYER
   ↓
   ├─ Dashboard UI (Streamlit)
   ├─ Battery Health Reports (CSV/JSON/PDF)
   └─ Regulatory Compliance Reports

7. STAKEHOLDER ACCESS
   ↓
   ├─ Vehicle Owners - Monitor battery health
   ├─ Manufacturers - Verify warranty
   ├─ Recyclers - Access battery condition
   ├─ Regulators - Audit records
   └─ Resellers - Authenticate history
```

---

## 📊 Data Flow Example

### **Use Case 1: Store Battery Passport**
```
User: "Store this battery as EV Passport ID 12345"
System Flow:
  1. Create battery record in UI
  2. Generate QR code
  3. Call BatteryRegistry.registerBattery()
  4. Store on-chain metadata
  5. Return passport ID & QR code
System: "Battery stored successfully. Passport ID: EV-BATT-20260711-12345"
```

### **Use Case 2: Query Battery Health**
```
User: "What is the health of my battery?"
System Flow:
  1. User enters passport ID
  2. Query HealthRecordLedger.sol for latest health record
  3. Run health prediction model on historical data
  4. Display SoH (87%), SoC (65%), cycles (520)
  5. Show health status (GOOD) & trends
System: "Battery SoH is 87%, SoC 65%, cycles: 520. Status: GOOD (80-90%)"
```

---

## 🚀 Execution Steps (Complete System)

### **1. Environment Setup**
```bash
# Clone/navigate to project
cd c:\Users\arnav\EV BATTERY

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **2. Initialize Configuration**
```bash
# Create .env file
copy .env.example .env

# Update .env with:
WEB3_PROVIDER_URI=http://localhost:8545
PRIVATE_KEY=<your_private_key>
ACCOUNT_ADDRESS=<your_account>
```

### **3. Start Blockchain Node**
```bash
# Terminal 1: Start Ganache/Hardhat
docker-compose up

# Or locally:
npx hardhat node
```

### **4. Deploy Smart Contracts**
```bash
# Terminal 2: Deploy contracts
python blockchain_protocol/deployment/deploy_protocol.py
```

### **5. Initialize Battery Data** (Optional)
```bash
# Generate sample battery data
python scripts/battery_data_loader.py
```

### **6. Start Application**
```bash
# Terminal 3: Run Streamlit dashboard
streamlit run app.py
```

### **7. Access Dashboard**
```
Open browser: http://localhost:8501
Login: Username & Password (create account first)
```

---

## 📈 Performance Metrics to Track

| Metric | Target | Status |
|--------|--------|--------|
| Battery Health Prediction Accuracy | > 85% | ⏳ Pending |
| Anomaly Detection Precision | > 90% | ⏳ Pending |
| API Response Time | < 500ms | ⏳ Pending |
| Data Ingestion Latency | < 1 second | ⏳ Pending |
| Model Retraining Success Rate | 100% | ⏳ Pending |
| System Uptime | > 99% | ⏳ Pending |

---

## 🔐 Compliance & Standards

- ✅ **Battery Passport Directive (EU 2023/1542)**
- ✅ **SEBI Guidelines** (India - Securities Board)
- ✅ **Data Privacy:** Encryption, Access Control
- ✅ **Blockchain Immutability:** Audit Trail for regulators

---

## 📞 Key Files Reference

| File | Purpose | Status |
|------|---------|--------|
| `config.py` | System configuration | ✅ Updated |
| `app.py` | Main Streamlit app | ✅ Updated |
| `README.md` | Quick start | ✅ Updated |
| `requirements.txt` | Dependencies | ✅ Updated |
| `scripts/battery_data_loader.py` | Data ingestion | 🔄 To Create |
| `ai_oracle/training/battery_health_trainer.py` | ML model | 🔄 To Create |
| `contracts/BatteryRegistry.sol` | Smart contract | 🔄 To Create |
| `ui/pages/battery_records.py` | UI page | 🔄 To Create |

---

## 📋 Checklist for Completion

- [x] Update README.md
- [x] Update config.py
- [x] Update app.py
- [x] Update requirements.txt
- [x] Create alignment documentation
- [ ] Create battery data loader script
- [ ] Create battery health ML model
- [ ] Create smart contracts (BatteryRegistry, HealthLedger, CycleTracker, RecyclingRegistry)
- [ ] Create battery records UI page
- [ ] Create health analytics UI page
- [ ] Create QR code generator UI page
- [ ] Integrate IoT/MQTT data ingestion
- [ ] Implement battery data validation pipeline
- [ ] Add regulatory compliance reporting
- [ ] Deploy and test end-to-end

---

**Last Updated:** 2026-07-11  
**Next Review:** After Milestone 1 completion (Month 2)
