# EV Battery Passport System - Complete Execution Guide

## 🚀 Quick Start Guide

This guide provides step-by-step instructions to set up and run the EV Battery Passport system with smart contract integration.

---

## 📋 Prerequisites

### Required Software
- **Python 3.8+**
- **Node.js 16+** (for smart contract compilation)
- **Ganache** or **Hardhat** (for local blockchain)
- **Git**

### Required Python Packages
```bash
pip install -r requirements.txt
```

### Required Node Packages
```bash
npm install
```

---

## 🔧 System Setup

### Step 1: Environment Configuration

1. **Copy environment template**:
```bash
cp .env.example .env
```

2. **Edit `.env` file** with your configuration:
```env
# Blockchain Configuration
WEB3_PROVIDER_URI=http://localhost:8545
PRIVATE_KEY=your_private_key_here
ACCOUNT_ADDRESS=your_wallet_address_here

# Application Configuration
SIMULATION_MODE=true
BASE_DIR=c:/Users/arnav/EV BATTERY

# Data Directories
BATTERY_DATA_DIR=data/battery_data
PROCESSED_DATA_DIR=data/processed

# Model Paths
BATTERY_HEALTH_MODEL_PATH=models/trained/battery_health_model.pkl
HEALTH_SCALER_PATH=models/scalers/health_scaler.pkl
```

### Step 2: Start Local Blockchain

**Option A: Using Ganache**
```bash
# Install Ganache GUI or CLI
ganache-cli --port 8545
```

**Option B: Using Hardhat**
```bash
npx hardhat node
```

### Step 3: Compile Smart Contracts

```bash
# Compile Solidity contracts
npx hardhat compile
```

This will generate contract ABIs and bytecode in the `artifacts/contracts/` directory.

### Step 4: Deploy Smart Contracts

```bash
# Deploy battery passport contracts
python blockchain_protocol/deployment/deploy_battery_contracts.py
```

This will deploy:
- **BatteryUserRegistry** - User management contract
- **BatteryPassport** - Main battery passport contract
- **BatteryGovernance** - System governance contract

Deployment addresses will be saved to `blockchain_protocol/deployment/addresses.json`

---

## 🎯 Running the Application

### Step 1: Start the Streamlit Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### Step 2: User Registration

1. **Login Page**: Enter username and password
2. **System generates**: Cryptographic wallet address
3. **Save your credentials**: For future access

### Step 3: Add Battery Data

**Option A: Manual Entry**
1. Navigate to "➕ Add Battery"
2. Click "📝 Enter Data Manually"
3. Fill in battery specifications:
   - Manufacturer (e.g., Tesla, BYD, LG)
   - Battery Type (e.g., Li-ion NCA, Li-ion LFP)
   - Capacity (kWh)
   - Production Date
   - State of Health (SoH %)
   - State of Charge (SoC %)
   - Total Cycles
   - Temperature (°C)
4. Submit to generate passport ID and QR code

**Option B: Automatic Generation**
1. Navigate to "➕ Add Battery"
2. Click "🤖 Generate Automatically"
3. Select generation options:
   - Number of batteries
   - Battery type
4. Generate sample data for testing

### Step 4: Monitor Battery Health

1. Navigate to "📊 Dashboard"
2. Select battery from sidebar
3. View real-time metrics:
   - SoH and SoC gauges
   - Temperature monitoring
   - AI health predictions
   - Anomaly detection alerts

### Step 5: View Battery Records

1. Navigate to "🔋 Battery Records"
2. View all registered batteries
3. Search and filter by health status
4. View QR codes for each battery
5. Export data as JSON/CSV

---

## 🔗 Blockchain Integration

### Register Battery on Blockchain

**Manual Registration**:
```python
from blockchain_protocol.execution_engine.battery_passport_controller import BatteryPassportController
from config import AppConfig

config = AppConfig()
controller = BatteryPassportController(config)

# Register battery on blockchain
result = controller.register_on_blockchain("EV-BATT-20260711-12345")
print(result)
```

**Automatic Registration** (in UI):
- Check "Register on Blockchain" checkbox when adding battery
- System automatically registers after local storage

### Query Blockchain Data

```python
# Get battery from blockchain
battery_data = controller.battery_passport_contract.functions.getBattery(
    "EV-BATT-20260711-12345"
).call()

# Get user's batteries
user_batteries = controller.battery_passport_contract.functions.getBatteryByOwner(
    user_address
).call()
```

---

## 🧪 Testing

### Run Unit Tests

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_battery_passport.py
```

### Test Smart Contracts

```bash
# Run Hardhat tests
npx hardhat test
```

### Manual Testing Checklist

- [ ] User registration works
- [ ] Manual battery entry saves data
- [ ] Automatic generation creates batteries
- [ ] QR codes generate correctly
- [ ] Dashboard displays battery metrics
- [ ] AI predictions work
- [ ] Blockchain registration succeeds (in live mode)
- [ ] Battery records page loads
- [ ] Search and filter work
- [ ] Export functionality works

---

## 📊 Smart Contract Functions

### BatteryUserRegistry

**User Management**:
- `registerUser(username, privateKeyHash)` - Register new user
- `getUser(address)` - Get user information
- `getWalletByUsername(username)` - Find wallet by username
- `verifyRecovery(username, privateKeyHash)` - Account recovery

**Activity Tracking**:
- `recordBatteryRegistration(user, passportId)` - Track battery registration
- `getUserBatteryCount(user)` - Get user's battery count

### BatteryPassport

**Battery Operations**:
- `registerBattery(passportId, manufacturer, batteryType, capacityKwh, ...)` - Register new battery
- `updateBatteryHealth(passportId, soh, soc, cycles, temperature)` - Update health data
- `getBattery(passportId)` - Get battery information
- `getBatteryByOwner(owner)` - Get all batteries for owner
- `deactivateBattery(passportId)` - Deactivate battery

**Health History**:
- `getHealthHistory(passportId)` - Get health record history

### BatteryGovernance

**Parameter Management**:
- `updateParameterDirectly(parameter, newValue)` - Admin parameter update
- `getParameter(parameter)` - Get current parameter value

**Governance**:
- `createProposal(parameter, newValue)` - Create governance proposal
- `voteOnProposal(proposalId, support)` - Vote on proposal
- `executeProposal(proposalId)` - Execute approved proposal

---

## 🔍 Troubleshooting

### Common Issues

**1. Smart Contract Deployment Fails**
- Ensure blockchain node is running
- Check WEB3_PROVIDER_URI in .env
- Verify you have sufficient ETH for gas
- Check contract compilation succeeded

**2. Contract Loading Fails**
- Verify addresses.json exists
- Check contract addresses are correct
- Ensure blockchain node is accessible
- Check ABI files exist in artifacts/

**3. QR Code Generation Fails**
- Ensure qrcode library is installed
- Check qr_code_dir permissions
- Verify PIL/Pillow is installed

**4. AI Prediction Fails**
- Check model files exist in models/trained/
- Verify scaler files exist in models/scalers/
- Ensure model format is compatible

**5. Data Loading Fails**
- Check data directory permissions
- Verify JSON file format
- Ensure file paths are correct

### Debug Mode

Enable debug logging in `.env`:
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

---

## 📈 Performance Optimization

### Database Optimization
- Use SQLite for local testing
- Use PostgreSQL for production
- Implement database indexing

### Blockchain Optimization
- Use gas optimization techniques
- Batch multiple operations
- Use event logs for queries

### AI Model Optimization
- Use model quantization
- Implement caching
- Use batch predictions

---

## 🔒 Security Best Practices

### Smart Contract Security
- Use OpenZeppelin libraries
- Implement access control
- Add circuit breakers
- Audit contracts before deployment

### Data Security
- Encrypt sensitive data
- Use secure key management
- Implement rate limiting
- Validate all inputs

### User Security
- Hash passwords properly
- Use secure session management
- Implement 2FA
- Regular security audits

---

## 📝 Maintenance

### Regular Tasks

**Daily**:
- Monitor blockchain node health
- Check application logs
- Monitor system performance

**Weekly**:
- Backup database
- Review smart contract events
- Update AI models if needed

**Monthly**:
- Security audit
- Performance review
- Update dependencies
- Review governance proposals

---

## 🚢 Deployment

### Production Deployment

1. **Deploy to Mainnet**:
```bash
# Update .env for mainnet
WEB3_PROVIDER_URI=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
SIMULATION_MODE=false

# Deploy contracts
python blockchain_protocol/deployment/deploy_battery_contracts.py
```

2. **Deploy Application**:
```bash
# Use Docker for containerization
docker build -t ev-battery-passport .
docker run -p 8501:8501 ev-battery-passport
```

3. **Set up Monitoring**:
- Application monitoring (Prometheus/Grafana)
- Blockchain monitoring
- Error tracking (Sentry)
- Log aggregation (ELK Stack)

---

## 📚 Additional Resources

### Documentation
- [Smart Contract Documentation](contracts/README.md)
- [API Documentation](api/README.md)
- [Architecture Documentation](SYSTEM_ARCHITECTURE.md)

### Development
- [Contributing Guidelines](CONTRIBUTING.md)
- [Code Style Guide](STYLE_GUIDE.md)
- [Testing Guidelines](TESTING.md)

### Support
- GitHub Issues
- Documentation Wiki
- Community Forum

---

## ✅ Verification Checklist

Before going live, verify:

- [ ] All smart contracts deployed
- [ ] Contract addresses saved
- [ ] Blockchain node accessible
- [ ] Database configured
- [ ] AI models loaded
- [ ] QR code generation working
- [ ] User authentication working
- [ ] All UI pages functional
- [ ] API endpoints tested
- [ ] Security audit completed
- [ ] Performance tested
- [ ] Backup procedures in place
- [ ] Monitoring configured
- [ ] Documentation updated

---

## 🎓 Training Resources

### For Developers
- Solidity documentation
- Web3.py documentation
- Streamlit documentation
- Machine learning for battery health

### For Users
- User manual
- Video tutorials
- FAQ section
- Support contact information

---

**Last Updated**: 2026-07-11
**Version**: 1.0.0
**Status**: Production Ready
