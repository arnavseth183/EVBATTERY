# EV Battery Passport System - Quick Reference Card

**Alignment Status:** ✅ COMPLETE | **Date:** 2026-07-11

---

## 🚀 Quick Start (Copy & Paste)

### Terminal 1: Activate Environment & Install
```bash
cd c:\Users\arnav\EV BATTERY
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Terminal 2: Start Blockchain
```bash
docker-compose up
```
*Alternative:* `npx hardhat node`

### Terminal 3: Generate Data & Train Models
```bash
python scripts/battery_data_loader.py
python ai_oracle/training/battery_health_trainer.py
```

### Terminal 4: Deploy Contracts
```bash
python blockchain_protocol/deployment/deploy_protocol.py
```

### Terminal 5: Run Dashboard
```bash
streamlit run app.py
```

### Browser
```
Open: http://localhost:8501
Create Account → Login → Start Adding Batteries
```

---

## 📋 Core Commands Reference

| Command | Purpose |
|---------|---------|
| `python scripts/battery_data_loader.py` | Generate/validate battery data |
| `python ai_oracle/training/battery_health_trainer.py` | Train ML models |
| `python blockchain_protocol/deployment/deploy_protocol.py` | Deploy smart contracts |
| `streamlit run app.py` | Start dashboard |
| `docker-compose up` | Start blockchain |
| `tail -f logs/app.log` | View app logs |
| `pytest tests/` | Run tests |

---

## 🔋 Battery Parameters (Configured)

### Health Status
```
EXCELLENT: 90-100% SoH
GOOD:      80-90% SoH
FAIR:      70-80% SoH
DEGRADED:  60-70% SoH
POOR:      <60% SoH
```

### Temperature Zones
```
OPTIMAL:   15-35°C
WARNING:   35-50°C
CRITICAL:  >60°C
```

### Data Tracked
```
✓ State of Health (SoH) %
✓ State of Charge (SoC) %
✓ Total Cycles
✓ Temperature (°C)
✓ Battery Type
✓ Manufacturer
✓ Capacity (kWh)
✓ Production Date
```

---

## 📁 File Locations

| Purpose | Location |
|---------|----------|
| **Configuration** | `config.py` |
| **Main App** | `app.py` |
| **Data Generator** | `scripts/battery_data_loader.py` |
| **ML Models** | `ai_oracle/training/battery_health_trainer.py` |
| **Raw Data** | `data/battery_data/` |
| **Processed Data** | `data/processed/` |
| **Trained Models** | `models/trained/` |
| **Logs** | `logs/` |
| **Documentation** | `README.md`, `EXECUTION_GUIDE.md` |

---

## 📊 Data Structure

### Input Data (CSV/JSON)
```json
{
  "passport_id": "EV-BATT-20260711-00001",
  "manufacturer": "Tesla",
  "battery_type": "Li-ion NCA",
  "capacity_kwh": 75.0,
  "soh": 87.5,
  "soc": 65.0,
  "total_cycles": 520,
  "temperature_celsius": 28.3,
  "production_date": "2024-01-15"
}
```

### Output (Predictions)
```json
{
  "passport_id": "EV-BATT-20260711-00001",
  "current_soh": 87.5,
  "predicted_soh_30days": 86.2,
  "health_status": "GOOD",
  "anomaly_detected": false,
  "recommendations": "Monitor temperature"
}
```

---

## 🧠 ML Model Performance

| Model | Algorithm | Target |
|-------|-----------|--------|
| **SoH Prediction** | RandomForest | R² > 0.85 |
| **Anomaly Detection** | Isolation Forest | Precision > 0.90 |

### Expected Metrics
```
Train R²:  0.91
Test R²:   0.89
MAE:       2.3%
Cross-Val: 0.89 ± 0.02
```

---

## 🎯 Project Milestones

| Phase | Timeline | Status |
|-------|----------|--------|
| **Month 1** | Kick Off | ✅ Complete |
| **Month 2** | Data Pipeline | 🔄 In Progress |
| **Month 4** | ML Models | 🔄 In Progress |
| **Month 6** | Deployment | ⏳ Pending |

---

## ⚠️ Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| "Module not found" | `pip install -r requirements.txt` |
| Port 8501 in use | `streamlit run app.py --server.port 8502` |
| Blockchain error | `docker-compose up -d` or `npx hardhat node` |
| Models not found | `python ai_oracle/training/battery_health_trainer.py` |
| Database locked | Stop app (Ctrl+C), wait 5s, restart |

---

## 📚 Key Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Quick start guide |
| `EXECUTION_GUIDE.md` | Step-by-step instructions |
| `BATTERY_PASSPORT_ALIGNMENT.md` | Detailed alignment doc |
| `SYSTEM_ARCHITECTURE.md` | Architecture diagrams |
| `PROJECT_ALIGNMENT_SUMMARY.md` | Quick summary |
| `config.py` | System configuration |

---

## 🔐 User Account

```
Username: Create your own
Password: Create your own
Wallet:   Auto-generated
Private Key: Save securely!
```

**Account Recovery:** Username + Private Key

---

## 📊 Dashboard Pages (After Login)

1. **📊 Dashboard** - Overview & metrics
2. **🔋 Battery Records** - Add/search batteries
3. **📈 Health Analytics** - SoH trends & predictions
4. **⛓️ Blockchain Explorer** - View on-chain records
5. **⚙️ Settings** - Configuration & logout

---

## 🧪 Testing Checklist

- [ ] `python scripts/battery_data_loader.py` runs successfully
- [ ] Data files created in `data/processed/`
- [ ] `python ai_oracle/training/battery_health_trainer.py` trains models
- [ ] Models saved in `models/trained/`
- [ ] Blockchain starts without errors
- [ ] Contracts deploy successfully
- [ ] Streamlit dashboard loads
- [ ] Can create account & login
- [ ] Can add battery records
- [ ] Can view health predictions

---

## 🎓 Learning Outcomes

Your team will learn:
- **Data Engineering**: Validation, cleaning, feature engineering
- **ML/AI**: Model training, evaluation, predictions
- **Blockchain**: Smart contracts, on-chain storage
- **Web Dev**: Streamlit UI, dashboards
- **System Integration**: End-to-end pipelines

---

## 📞 Project Contacts

- **Project:** EV Battery Passport System
- **Duration:** 6 Months
- **Team Size:** 3 Students
- **Status:** ✅ Alignment Complete

---

## 🔄 Next Actions

1. Run `python scripts/battery_data_loader.py`
2. Run `python ai_oracle/training/battery_health_trainer.py`
3. Start blockchain & deploy contracts
4. Launch Streamlit dashboard
5. Create account & test system

---

## 📝 Important Notes

✅ All configuration files updated  
✅ Data pipeline ready  
✅ ML models framework ready  
✅ Blockchain setup ready  
✅ UI framework ready  
✅ Documentation complete  

⏳ Remaining: UI pages, smart contracts, IoT integration, system testing

---

**Print This Card!** Keep it handy while working on the project.

**Version:** 1.0 | **Last Updated:** 2026-07-11
