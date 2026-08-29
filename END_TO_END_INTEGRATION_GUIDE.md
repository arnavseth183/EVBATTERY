# 🚀 DAPPTRADE End-to-End Integration Guide

## Quick Start (TL;DR)

```bash
# Terminal 1: Start blockchain
npx hardhat node

# Terminal 2: Deploy contracts
npx hardhat run scripts/deploy.js --network localhost

# Terminal 3: Run integration tests
python scripts/integration_test.py

# Terminal 4: Start UI
streamlit run app.py
```

---

## 📋 Prerequisites

- [x] Python 3.9+
- [x] Node.js 16+
- [x] Hardhat installed (`npm install`)
- [x] `requirements.txt` dependencies installed
- [x] `.env` file configured

---

## 🔧 Step-by-Step Setup

### Step 1: Configure Environment

**File:** `.env`

```bash
NETWORK=local
WEB3_PROVIDER_URI=http://127.0.0.1:8545
PRIVATE_KEY=0x...  # Get from hardhat node
ACCOUNT_ADDRESS=0x...  # Get from hardhat node
```

To get accounts from hardhat:
```bash
npx hardhat node
# Look at the console output for account addresses and private keys
```

---

### Step 2: Start Blockchain Node

```bash
npx hardhat node
```

This will:
- Start local Ethereum node at `http://127.0.0.1:8545`
- Create 20 test accounts with 10,000 ETH each
- Show account addresses and private keys in console

**Output Example:**
```
hardhat_devnet running at http://127.0.0.1:8545

Accounts (first 2):
Account #0: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
Private Key: 0xac0974bec39a17e36ba4a6b4d238ff944bacb476cac3eca36233ced9dacbe515
...
```

---

### Step 3: Deploy Smart Contracts

```bash
npx hardhat run scripts/deploy.js --network localhost
```

This will:
- Compile all contracts
- Deploy to local node
- Save contract addresses to `blockchain_protocol/deployment/addresses.json`

**After deployment, verify addresses.json:**

```bash
cat blockchain_protocol/deployment/addresses.json
```

Should contain:
```json
{
    "TradingProtocol": "0x...",
    "PortfolioManager": "0x...",
    "Ledger": "0x...",
    "Governance": "0x...",
    "RiskManager": "0x..."
}
```

---

### Step 4: Configure Python

#### 4a. Create Virtual Environment (Recommended)

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Mac/Linux
source venv/bin/activate
```

#### 4b. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4c. Update `.env` with Hardhat Accounts

Copy a private key from hardhat node output and add to `.env`:

```bash
PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb476cac3eca36233ced9dacbe515
ACCOUNT_ADDRESS=0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
```

---

### Step 5: Run Integration Tests

```bash
python scripts/integration_test.py
```

This will verify:
- ✅ Web3 connection to blockchain node
- ✅ Contract loader functionality
- ✅ Protocol controller initialization
- ✅ Trade execution (simulation)
- ✅ Portfolio history tracking
- ✅ Risk metrics calculation
- ✅ User registry
- ✅ Governance functionality

**Expected Output:**
```
✅ PASS | Web3 Connection
✅ PASS | Contract Addresses
✅ PASS | Load TradingProtocol
...
[TEST SUMMARY]
✅ Passed: 15
❌ Failed: 0
Success Rate: 100.0%
```

---

### Step 6: Start Streamlit UI

```bash
streamlit run app.py
```

This will:
- Open browser at `http://localhost:8501`
- Show login page
- Allow you to create account and start trading

---

## 🔗 Architecture Overview

```
Streamlit UI (app.py)
        ↓
ProtocolController (blockchain_protocol/execution_engine/)
        ↓
Web3 Provider (blockchain_protocol/web3_layer/)
        ↓
Smart Contracts (contracts/*.sol)
        ↓
Local Blockchain Node (http://127.0.0.1:8545)
```

### Data Flow for a Trade

```
1. User selects stock → AI generates signal
2. Trade Panel calls protocol.execute_trade()
3. ProtocolController.execute_trade() called
4. In simulation mode:
   - Portfolio state updated locally
   - Portfolio history appended
5. In live mode:
   - TradeExecutor calls TradingProtocol.openPosition()
   - Transaction sent to blockchain
   - Ledger.recordTrade() called
   - Event emitted by smart contract
6. Risk Dashboard reads portfolio history
7. Metrics calculated from historical data
```

---

## 🧪 Testing the System

### Test 1: Create Account & Login

1. Open Streamlit UI
2. Go to "Create Account" tab
3. Enter username and password
4. Copy wallet address and private key
5. Login with credentials

### Test 2: Execute Trade

1. Login with your account
2. Select stock (e.g., RELIANCE.NS)
3. AI signal generated automatically
4. Click "Execute Trade" button
5. Trade executed, portfolio updated
6. Check portfolio value increased/decreased

### Test 3: View Risk Dashboard

1. Navigate to "Risk Dashboard" page
2. Should show risk metrics:
   - Total Return (%)
   - Sharpe Ratio
   - Max Drawdown
   - VaR & CVaR
3. Risk classification (Low/Moderate/High)

### Test 4: Governance

1. Navigate to "Governance" page
2. View protocol parameters
3. Change max_position_size to 150
4. Submit proposal
5. Should see transaction hash

### Test 5: Monitor Transactions

1. Navigate to "Blockchain Explorer"
2. See all executed trades
3. Each trade shows:
   - Stock symbol
   - Buy/Sell action
   - Quantity and price
   - Transaction status

---

## 🐛 Troubleshooting

### Problem: "Blockchain node connection failed"

**Solution:**
```bash
# Make sure hardhat node is running in terminal 1
npx hardhat node
```

### Problem: "Contracts not deployed"

**Solution:**
1. Verify contracts deployed:
```bash
cat blockchain_protocol/deployment/addresses.json
```

2. If empty or missing, redeploy:
```bash
npx hardhat run scripts/deploy.js --network localhost
```

### Problem: "Not enough data to compute metrics"

**Solution:**
- Execute at least 2 trades to generate history
- Risk Dashboard needs history points to calculate metrics

### Problem: "Invalid contract address"

**Solution:**
1. Clear browser cache (Streamlit session)
2. Restart Streamlit: `Ctrl+C` then `streamlit run app.py`
3. Check addresses.json is valid JSON

### Problem: "Port 8545 already in use"

**Solution:**
```bash
# Kill process using port 8545
# On Windows
netstat -ano | findstr :8545
taskkill /PID <PID> /F

# On Mac/Linux
lsof -i :8545
kill -9 <PID>
```

---

## 📊 Key Files Modified/Created

### Core Integration Files

| File | Purpose |
|------|---------|
| `blockchain_protocol/execution_engine/protocol_controller.py` | Main blockchain controller with Web3 integration |
| `blockchain_protocol/web3_layer/contract_loader.py` | Load contracts from addresses.json |
| `scripts/integration_test.py` | End-to-end integration tests |
| `blockchain_protocol/deployment/addresses.json` | Contract addresses (auto-generated) |

### UI Files Updated

| File | Changes |
|------|---------|
| `ui/pages/risk_dashboard.py` | Now reads portfolio history from protocol |
| `ui/pages/governance.py` | Fixed parameter protocol parameter handling |
| `ui/pages/trade_panel.py` | Records trades on Ledger.sol |

### Contract Files

| File | Role |
|------|------|
| `contracts/TradingProtocol.sol` | Executes trades, applies confidence filters |
| `contracts/Ledger.sol` | Records trades permanently on-chain |
| `contracts/Governance.sol` | Protocol parameter governance |
| `contracts/PortfolioManager.sol` | Tracks portfolio value & PnL |

---

## ✅ Verification Checklist

Use this to verify your setup is working:

- [ ] Hardhat node running (`http://127.0.0.1:8545`)
- [ ] Contracts deployed (check `addresses.json`)
- [ ] `.env` file configured with valid addresses
- [ ] Integration tests passing (100% success rate)
- [ ] Streamlit app runs without errors
- [ ] Can create account and login
- [ ] Can execute trades and see portfolio update
- [ ] Risk dashboard shows metrics
- [ ] Governance allows parameter proposals
- [ ] Transaction history visible

---

## 🎯 What's Now Connected (End-to-End)

### ✅ Trade Execution Path
- User selects stock → Signal generated → Portfolio updated → History tracked

### ✅ Risk Metrics Path
- Portfolio history → Risk calculations → Dashboard displays metrics

### ✅ Governance Path
- Parameter proposal → Blockchain transaction → Local state updated

### ✅ Ledger Recording Path  
- Trade executed → Ledger.recordTrade() called → Trade recorded on blockchain

### ✅ User Management Path
- Create account → Wallet generated → User registry stored → Authentication works

---

## 📈 Next Steps

After verification, you can:

1. **Train ML Model**: Place model files in `models/trained/`
2. **Configure Live Blockchain**: Update `.env` to use testnet RPC
3. **Implement Settlement**: Connect to actual payment processors
4. **Add More Stocks**: Extend `SUPPORTED_STOCKS` in config.py
5. **Deploy to Production**: Use Ethereum mainnet contracts

---

## 📞 Support & Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Transaction Logs

```bash
tail -f logs/transactions.log
```

### View Integration Test Results

```bash
cat tests/integration_results.json
```

### Clear Session State

```bash
rm -rf ~/.streamlit/
```

---

## 🔐 Security Notes

**⚠️ WARNING:**
- `.env` file contains private keys
- NEVER commit `.env` to version control
- NEVER share private keys
- Use testnet only during development
- Move to mainnet only after thorough testing

---

**Happy Trading! 🚀**

For issues, check logs in the `logs/` directory or run integration tests again.
