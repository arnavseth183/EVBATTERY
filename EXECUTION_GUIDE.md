# EV Battery Passport System - Complete Execution Guide

**Project:** EV Battery Passport System  
**Duration:** 6 Months  
**Team Size:** 3 Students  
**Last Updated:** 2026-07-11

---

## 📋 Quick Start (5 Minutes)

### Step 1: Environment Setup
```bash
# Navigate to project directory
cd c:\Users\arnav\EV BATTERY

# Create Python virtual environment
python -m venv venv

# Activate environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configuration
```bash
# Create .env file
copy .env.example .env  (or create manually)

# Add the following to .env:
WEB3_PROVIDER_URI=http://localhost:8545
PRIVATE_KEY=your_private_key_here
ACCOUNT_ADDRESS=your_account_address_here
ENCRYPTION_SECRET=your_secret_key
```

### Step 3: Start Services
```bash
# Terminal 1: Start blockchain node
docker-compose up

# Or use local Hardhat:
npx hardhat node
```

### Step 4: Deploy Contracts
```bash
# Terminal 2: Deploy smart contracts
python blockchain_protocol/deployment/deploy_protocol.py
```

### Step 5: Run Application
```bash
# Terminal 3: Start Streamlit dashboard
streamlit run app.py
```

### Step 6: Access Dashboard
```
Open browser: http://localhost:8501
Create account or login
```

---

## 🔍 Detailed Execution Steps

### **Phase 1: Battery Data Processing** (Month 1-2)

#### Step 1.1: Generate Sample Battery Data
```bash
python scripts/battery_data_loader.py
```

**Output:**
- `data/processed/battery_data_processed.csv` (100 records)
- `data/processed/battery_data_processed.json` (Same, JSON format)
- `data/processed/battery_report_YYYYMMDD_HHMMSS.json` (Statistics)

**What it does:**
- Generates synthetic EV battery data (100 records)
- Validates each record against schema
- Computes degradation rates
- Classifies health status (EXCELLENT, GOOD, FAIR, DEGRADED, POOR)
- Exports to CSV/JSON formats

**Expected Output:**
```
Generating 100 sample battery records...
✓ Generated 100 battery records

Validating battery records...
✓ 100/100 records are valid

Preprocessing battery data...
✓ Preprocessing complete

Saving processed data...
✓ Data saved to:
  - data/processed/battery_data_processed.csv
  - data/processed/battery_data_processed.json

Battery Statistics:
  Total Batteries: 100
  Average SoH: 87.34%
  Average Cycles: 520
  Average Temperature: 28.3°C
  
  Health Status Breakdown:
    - EXCELLENT: 25
    - GOOD: 40
    - FAIR: 20
    - DEGRADED: 12
    - POOR: 3

✅ Battery data loading and preprocessing complete!
```

---

#### Step 1.2: Train Battery Health Models
```bash
python ai_oracle/training/battery_health_trainer.py
```

**Output:**
- `models/trained/battery_health_model_YYYYMMDD_HHMMSS.pkl` (Prediction model)
- `models/trained/anomaly_model_YYYYMMDD_HHMMSS.pkl` (Anomaly detection)
- `models/scalers/health_scaler_YYYYMMDD_HHMMSS.pkl` (Feature scaler)
- `models/scalers/anomaly_scaler_YYYYMMDD_HHMMSS.pkl` (Anomaly scaler)
- `models/trained/training_history_YYYYMMDD_HHMMSS.pkl` (Metrics)

**What it does:**
- Loads processed battery data
- Creates features (cycles, temperature, degradation rate, etc.)
- Trains RandomForest for SoH prediction
- Trains Isolation Forest for anomaly detection
- Evaluates models with cross-validation
- Saves all models and scalers

**Expected Output:**
```
Training Results:
  Train MSE: 12.3456, Test MSE: 15.6789
  Train MAE: 2.3456, Test MAE: 3.1234
  Train R²: 0.9123, Test R²: 0.8945
  Cross-validation R² (5-fold): 0.8876 (+/- 0.0234)

Anomaly Detection Results:
  Detected anomalies: 10/200 (5.00%)
  Mean anomaly score: -0.4567

✓ Health model saved: models/trained/battery_health_model_20260711_120000.pkl
✓ Anomaly model saved: models/trained/anomaly_model_20260711_120000.pkl
```

---

### **Phase 2: Blockchain Setup** (Month 2-3)

#### Step 2.1: Deploy Smart Contracts
```bash
python blockchain_protocol/deployment/deploy_protocol.py
```

**Output:**
- `blockchain_protocol/deployment/addresses.json` (Contract addresses)
- Console logs with deployed contract addresses

**What it does:**
- Compiles Solidity contracts
- Deploys to local Hardhat/Ganache node
- Registers contract addresses
- Initializes contract storage

**Expected Output:**
```
Deploying smart contracts...
✓ BatteryRegistry deployed at: 0x1234...abcd
✓ HealthRecordLedger deployed at: 0x5678...efgh
✓ CycleTracker deployed at: 0xabcd...1234
✓ RecyclingRegistry deployed at: 0xefgh...5678

addresses.json updated with deployed contract addresses
```

---

### **Phase 3: Application Startup** (Month 3-6)

#### Step 3.1: Start Streamlit Dashboard
```bash
streamlit run app.py
```

**What happens:**
1. Loads configuration from `config.py`
2. Initializes database and directories
3. Starts web server on http://localhost:8501
4. Loads ML models (if available)
5. Connects to blockchain node

**First Access:**
```
Dashboard opens at: http://localhost:8501

Pages Available:
  📊 Dashboard - Overview of all batteries
  🔋 Battery Records - Manage battery passports
  📈 Health Analytics - SoH trends and predictions
  ⛓️ Blockchain Explorer - View on-chain records
  ⚙️ Settings - System configuration
```

---

#### Step 3.2: Create User Account

1. **Go to Login Page**
   - Click on "📝 Create Account" tab
   - Enter Username and Password
   - Click "Create Account"

2. **Save Private Key**
   - Private key will be displayed (save securely!)
   - This key is needed for account recovery

3. **Login**
   - Use created username and password
   - Enter the Battery Passport System

---

#### Step 3.3: Store Battery Passport

1. **Go to Battery Records**
   - Click "🔋 Battery Records" in sidebar
   - Click "Add New Battery"

2. **Enter Battery Information**
   - Passport ID (auto-generated or manual)
   - Manufacturer (Tesla, BYD, LG, etc.)
   - Battery Type (Li-ion NCM, LFP, etc.)
   - Capacity (kWh)
   - Production Date
   - Current SoH, SoC, Cycles, Temperature

3. **Submit**
   - Battery data stored on-chain
   - QR code generated
   - Confirmation message displayed

---

#### Step 3.4: Query Battery Health

1. **Go to Battery Records**
   - Find battery by Passport ID
   - Click to view details

2. **View Health Status**
   - Current SoH % (State of Health)
   - Current SoC % (State of Charge)
   - Total cycles used
   - Temperature
   - Health classification (EXCELLENT, GOOD, etc.)

3. **View Predictions**
   - AI predicted SoH degradation
   - Time to next maintenance
   - Anomaly detection status

---

#### Step 3.5: Export Reports

1. **Go to Health Analytics**
   - Select date range
   - Click "Export Report"

2. **Available Formats**
   - CSV (comma-separated values)
   - JSON (structured format)
   - PDF (printable)

---

### **Phase 4: Maintenance & Monitoring** (Ongoing)

#### Step 4.1: Monitor System Health
```bash
# Check logs
tail -f logs/app.log
tail -f logs/battery_health.log
tail -f logs/blockchain.log
tail -f logs/data_ingestion.log
```

#### Step 4.2: Retrain Models Monthly
```bash
# Run model retraining
python ai_oracle/training/battery_health_trainer.py
```

#### Step 4.3: Backup Data
```bash
# Backup processed data
copy data/processed data/backup_%DATE%
```

---

## 🧪 Testing & Validation

### Test 1: Data Pipeline
```bash
# Verify data loader works
python -c "from scripts.battery_data_loader import BatteryDataLoader; loader = BatteryDataLoader(); print('✓ Data loader OK')"
```

### Test 2: Model Training
```bash
# Verify model trainer works
python -c "from ai_oracle.training.battery_health_trainer import BatteryHealthTrainer; trainer = BatteryHealthTrainer(); print('✓ Model trainer OK')"
```

### Test 3: Blockchain Connection
```bash
# Test blockchain connection
python -c "from blockchain_protocol.web3_layer.web3_provider import get_web3_connection; w3 = get_web3_connection(); print(f'✓ Connected to {w3.eth.chain_id}')"
```

### Test 4: Database
```bash
# Verify database initialization
python -c "from blockchain_protocol.storage.user_wallet_registry import UserWalletRegistry; reg = UserWalletRegistry(); print('✓ Database OK')"
```

---

## 📊 Data Structure Examples

### Battery Record (Stored on-chain)
```json
{
  "passport_id": "EV-BATT-20260711-00001",
  "manufacturer": "Tesla",
  "battery_type": "Li-ion NCA",
  "capacity_kwh": 75.0,
  "production_date": "2024-01-15",
  "registration_timestamp": "2026-07-11T10:30:00Z",
  "owner_wallet": "0x1234...abcd"
}
```

### Health Record (Appended to ledger)
```json
{
  "passport_id": "EV-BATT-20260711-00001",
  "timestamp": "2026-07-11T15:45:00Z",
  "soh": 87.5,
  "soc": 65.0,
  "total_cycles": 520,
  "temperature_celsius": 28.3,
  "health_status": "GOOD",
  "predicted_soh_next_month": 86.2,
  "anomaly_detected": false
}
```

---

## 🐛 Troubleshooting

### Issue 1: "Module not found" errors
```bash
# Solution: Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### Issue 2: Blockchain connection failed
```bash
# Solution: Verify Ganache/Hardhat is running
docker ps  # Check if container is running
docker-compose up -d  # Start if not running
```

### Issue 3: Port 8501 already in use
```bash
# Solution: Use different port
streamlit run app.py --server.port 8502
```

### Issue 4: Models not loading
```bash
# Solution: Retrain models
python ai_oracle/training/battery_health_trainer.py
```

### Issue 5: Database locked error
```bash
# Solution: Stop app and restart
# Press Ctrl+C to stop
# Wait 5 seconds
# Run: streamlit run app.py
```

---

## 📈 Expected Milestones

### Month 1 (Kick Off)
- ✅ Project understanding & requirements
- ✅ Configuration files setup
- ✅ Directory structure created
- Target: Document project scope

### Month 2 (Milestone 1)
- 📌 Generate 1000+ battery data records
- 📌 Create data validation pipeline
- 📌 Feature engineering complete
- Target: 100% data quality

### Month 3 (Continuation)
- 📌 Deploy smart contracts
- 📌 Test blockchain integration
- 📌 Create user authentication
- Target: Blockchain fully functional

### Month 4 (Milestone 2)
- 📌 Train ML models (>85% accuracy)
- 📌 Anomaly detection working
- 📌 Create UI pages for battery management
- Target: AI models in production

### Month 5 (Integration)
- 📌 End-to-end system testing
- 📌 Regulatory compliance verification
- 📌 Performance optimization
- Target: System ready for deployment

### Month 6 (Closure)
- 📌 Deploy production system
- 📌 Generate final reports
- 📌 Team documentation
- Target: Project completion

---

## 📚 Project Structure Reference

```
c:\Users\arnav\EV BATTERY\
├── app.py                          # Main Streamlit application
├── config.py                       # Configuration (UPDATED ✅)
├── requirements.txt                # Dependencies (UPDATED ✅)
├── README.md                       # Quick start (UPDATED ✅)
│
├── ai_oracle/                      # ML/AI Components
│   ├── training/
│   │   └── battery_health_trainer.py  # Model training (NEW ✅)
│   ├── prediction/
│   ├── feature_engineering/
│   └── data_ingestion/
│
├── blockchain_protocol/            # Blockchain Integration
│   ├── deployment/
│   │   └── deploy_protocol.py
│   ├── execution_engine/
│   ├── web3_layer/
│   └── storage/
│
├── contracts/                      # Solidity Smart Contracts
│   ├── BatteryRegistry.sol         # Battery metadata
│   ├── HealthRecordLedger.sol      # Health history
│   ├── CycleTracker.sol            # Usage tracking
│   └── RecyclingRegistry.sol       # End-of-life
│
├── scripts/                        # Utility Scripts
│   ├── battery_data_loader.py      # Data ingestion (NEW ✅)
│   └── deploy.js
│
├── ui/                             # User Interface
│   ├── pages/
│   │   ├── dashboard.py
│   │   ├── portfolio.py
│   │   └── blockchain_explorer.py
│   └── components/
│
├── data/                           # Data Storage
│   ├── battery_data/               # Raw battery data
│   ├── processed/                  # Processed datasets
│   └── backup/                     # Backups
│
├── models/                         # ML Models
│   ├── trained/
│   │   ├── battery_health_model.pkl
│   │   └── anomaly_model.pkl
│   └── scalers/
│       ├── health_scaler.pkl
│       └── anomaly_scaler.pkl
│
├── logs/                           # Application Logs
│   ├── app.log
│   ├── battery_health.log
│   ├── blockchain.log
│   └── data_ingestion.log
│
└── BATTERY_PASSPORT_ALIGNMENT.md   # Alignment guide (NEW ✅)
```

---

## 🚀 Next Steps for Your Team

1. **Week 1**: Set up environment & test data pipeline
2. **Week 2**: Train ML models & evaluate performance
3. **Week 3**: Deploy smart contracts & test blockchain
4. **Week 4**: Build UI pages for battery management
5. **Weeks 5-6**: Integration testing & deployment

---

## 📞 Quick Reference Commands

```bash
# Activate environment
venv\Scripts\activate

# Start blockchain
docker-compose up

# Deploy contracts
python blockchain_protocol/deployment/deploy_protocol.py

# Generate data
python scripts/battery_data_loader.py

# Train models
python ai_oracle/training/battery_health_trainer.py

# Run dashboard
streamlit run app.py

# Check logs
tail -f logs/app.log

# Run tests
pytest tests/

# Stop all services
docker-compose down
```

---

**Version:** 1.0  
**Status:** ✅ Ready for Execution  
**Last Updated:** 2026-07-11  

**Questions?** Refer to README.md or BATTERY_PASSPORT_ALIGNMENT.md
