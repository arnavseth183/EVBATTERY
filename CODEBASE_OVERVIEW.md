# EV Battery Passport: Comprehensive Codebase Overview

## 1. PROJECT NAME & PURPOSE

**Project Name:** EV Battery Passport System  
**Full Name:** Decentralized EV Battery Lifecycle & Traceability Platform

**Purpose:**
The EV Battery Passport System combines **AI-powered battery health prediction** with **blockchain-based immutable record storage** to create a unified digital identity for EV batteries. It enables:

- **IoT/QR Data Ingestion** capturing battery manufacturing, usage, and recycling data
- **AI Health Prediction** for State of Health (SoH), State of Charge (SoC), cycle counting, and anomaly detection
- **Immutable Blockchain Records** for regulatory compliance and complete traceability
- **Query-based Access** for manufacturers, recyclers, owners, and regulators
- **End-to-End Lifecycle Tracking** from manufacturing through recycling
- **Real-time Interactive Dashboards** for battery passport monitoring and analysis

The core philosophy: **IoT captures data, AI predicts health, Blockchain verifies authenticity.**

---

## 2. MAIN MODULES & COMPONENTS

### 2.1 **AI Oracle Layer** (`ai_oracle/`)

The machine learning and signal generation system:

#### **Data Ingestion** (`ai_oracle/data_ingestion/`)
- `market_api_client.py`: Fetches OHLCV market data from Yahoo Finance API
- `nse_adapter.py`: NSE (National Stock Exchange) data adapter
- `data_cleaner.py`: Data validation and cleaning utilities
- `cache_manager.py`: Caching mechanism for market data

**Supported Stocks:** RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS, ICICIBANK.NS

#### **Feature Engineering** (`ai_oracle/feature_engineering/`)
- `indicators.py`: Computes technical indicators:
  - **SMA (Simple Moving Average)** - 14 period
  - **EMA (Exponential Moving Average)** - 14 period
  - **RSI (Relative Strength Index)** - momentum oscillator
  - **MACD (Moving Average Convergence Divergence)** - trend indicator
- `volatility.py`: Volatility calculations
- `pipeline.py`: Feature transformation pipeline
- `feature_builder.py`: Feature set construction

#### **Model Training** (`ai_oracle/training/`)
- `trainer.py`: Main model training orchestrator using RandomForestClassifier
  - 200 estimators, max depth 10
  - Binary classification (Buy/Sell)
  - 80/20 train/test split
- `retraining_pipeline.py`: Automated retraining on schedule
- `hyperparameter_search.py`: Optuna/Hyperopt based optimization
- `cross_validation.py`: K-fold validation

#### **Prediction Engine** (`ai_oracle/prediction/`)
- `predictor.py`: Real-time signal generation
  - Returns: `{"signal": "BUY|SELL|HOLD", "confidence": 0.0-1.0}`
  - **Confidence Threshold:** 0.65 (configurable)
  - Mock mode when model unavailable

---

### 2.2 **Blockchain Protocol Layer** (`blockchain_protocol/`)

Smart contract integration and execution engine:

#### **Smart Contract Suite** (`contracts/`)

| Contract | Purpose |
|----------|---------|
| **TradingProtocol.sol** | Core trading execution engine |
| **RiskManager.sol** | Position validation and liquidation logic |
| **PortfolioManager.sol** | Portfolio value & PnL calculation |
| **Governance.sol** | DAO-style parameter governance |
| **Ledger.sol** | Immutable trade audit trail |
| **UserRegistry.sol** | User account and wallet management |
| **ProtocolStorage.sol** | Shared data structures |
| **OracleInterface.sol** | Price feed integration |
| **CircuitBreaker.sol** | Emergency system pause mechanism |
| **GasSimulator.sol** | Fee simulation |

#### **Execution Engine** (`blockchain_protocol/execution_engine/`)
- `protocol_controller.py`: Main orchestrator
  - Trade execution (simulation + live modes)
  - Portfolio state management with history tracking
  - Contract loader and interaction
  - Governance parameter sync
  - Methods:
    - `execute_trade(signal_data)` → executes buy/sell/hold
    - `get_portfolio_state()` → returns cash, positions, history
    - `record_trade_on_ledger()` → records on blockchain
    - `enforce_rules()` → applies risk constraints
    - `propose_change()` → governance proposals

#### **Web3 Integration** (`blockchain_protocol/web3_layer/`)
- `web3_provider.py`: Connection to blockchain node (local Hardhat or remote)
- `contract_loader.py`: Loads compiled artifacts from Hardhat and instantiates contracts
- Supports artifact loading from `artifacts/contracts/` directory

#### **Storage & State** (`blockchain_protocol/storage/`)
- `user_wallet_registry.py`: User account database
  - User authentication
  - Balance tracking
  - Portfolio positions per user
  - Private key management

#### **Deployment** (`blockchain_protocol/deployment/`)
- `deploy_protocol.py`: Automated contract deployment script
- `addresses.json`: Contract address registry

---

### 2.3 **Smart Contracts Details** (`contracts/`)

#### **TradingProtocol.sol** (Core Engine)
```
Key Functions:
- openPosition(asset, size, collateral, isLong, confidence)
  * Validates AI confidence >= threshold
  * Applies risk constraints
  * Fetches oracle price
  * Applies slippage
  * Stores position

- closePosition(positionId, exitPrice)
  * Calculates PnL
  * Updates portfolio
  * Emits position closed event
```

#### **RiskManager.sol** (Risk Enforcement)
```
Features:
- Position validation (size, leverage, collateral checks)
- Liquidation logic (triggers when price hits threshold)
- Risk metrics:
  * Sharpe Ratio: (r̄ − rf) / σ
  * VaR (95%): Value at Risk percentile loss
  * CVaR (95%): Conditional Value at Risk (expected shortfall)
  * Max Drawdown: Peak-to-trough decline
  * Circuit breaker: ±40% price change triggers pause
```

#### **PortfolioManager.sol** (Portfolio Accounting)
```
Calculations:
Portfolio Value (V) = Σ (Quantity × Price) per position
PnL = (Exit Price − Entry Price) × Quantity

Features:
- Multi-position tracking
- Circuit breaker validation
- Real-time value calculation
- Risk-aware portfolio updates
```

#### **Governance.sol** (DAO-Style Governance)
```
Features:
- Proposal creation with parameter and value
- Voting mechanism (for/against)
- Execution after voting deadline
- Parameter changes include:
  * confidence_threshold (τ)
  * leverage limits
  * transaction costs
  * slippage percentages
  * circuit breaker thresholds
```

#### **Ledger.sol** (Audit Trail)
```
Immutable Records:
- Trade ID
- User address
- Symbol
- Buy/Sell action
- Price & quantity
- Timestamp
- AI confidence score

Tracks:
- Per-user trade history
- Asset positions with average entry price
- Cumulative PnL per user
```

---

### 2.4 **Security & Authentication** (`security/`, `auth/`)

- `encryption.py`: Data encryption utilities
- `key_manager.py`: Private key storage and retrieval
- `role_control.py`: User permission management
- `transaction_validation.py`: Transaction signature verification
- `wallet_auth.py`: Wallet authentication
- `wallet_generator.py`: New wallet generation with private keys
- `login_page.py`: User authentication interface

---

### 2.5 **User Interface** (`ui/`)

#### **Dashboard Pages** (`ui/pages/`)
| Page | Purpose |
|------|---------|
| **dashboard.py** | Main overview dashboard |
| **trade_panel.py** | Manual/auto trade execution interface |
| **portfolio.py** | Position tracking and analysis |
| **risk_dashboard.py** | Risk metrics and performance analysis |
| **blockchain_explorer.py** | Transaction history viewer |
| **governance.py** | Voting and proposal interface |
| **streamlit_login_page.py** | Authentication UI |

#### **Risk Dashboard Metrics**
```python
Metrics Computed from Portfolio History:

1. Total Return (%) = (End Value / Start Value - 1) × 100
2. Sharpe Ratio = √252 × (μ_returns - rf) / σ_returns
3. Sortino Ratio = √252 × (μ_returns - rf) / σ_downside
4. Max Drawdown (%) = (Peak - Trough) / Peak × 100
5. VaR (95%) = -Percentile(returns, 5)
6. CVaR (95%) = -Mean(returns[returns ≤ VaR])

Risk Classification:
- High Risk: Max Drawdown > 70%
- Moderate Risk: Max Drawdown 40-70%
- Low Risk: Max Drawdown < 40%
```

#### **Components** (`ui/components/`)
- `sidebar.py`: Navigation and portfolio summary

#### **Technology:**
- **Framework:** Streamlit (Python web framework)
- **Auto-Refresh:** st_autorefresh (10-second intervals)
- **Background:** Animated image carousel
- **Styling:** CSS and HTML integration

---

### 2.6 **Data & Database** (`data/`, `database/`)

- `user_db.py`: User database operations
- `live_price.py`: Real-time price tracking
- `user_wallets.json`: Wallet address storage
- **Subdirectories:**
  - `backtesting/`: Historical simulation data
  - `cache/`: Cached market data
  - `processed/`: Feature-engineered datasets
  - `raw/`: Raw market data from APIs

---

### 2.7 **Configuration & Logging**

#### **Configuration** (`config.py`)
```python
APP_NAME = "Decentralized AI Blockchain Trading"
SUPPORTED_STOCKS = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS"]
CONFIDENCE_THRESHOLD = 0.65
INITIAL_CAPITAL = 10000
INITIAL_ETH_BALANCE = 10000
GAS_LIMIT = 3000000
SIMULATION_MODE = True
```

#### **Logging** (`blockchain_protocol/logging_config.py`)
- Structured logging for:
  - AI predictions (`ai.log`)
  - Blockchain transactions (`blockchain.log`)
  - Trade execution (`transactions.log`)
  - Application events (`app.log`)

---

### 2.8 **Testing & Scripts** (`scripts/`, `tests/`)

#### **Deployment & Initialization:**
- `deploy.js`: Hardhat deployment script
- `initialize_balances.py`: Set initial user balances
- `seed_users.py`: Create test user accounts
- `start_local_node.sh`: Launch local blockchain

#### **Testing:**
- `integration_test.py`: End-to-end system tests
- `test_ai.py`: AI model tests
- `test_trading_protocol.py`: Smart contract tests
- `test_risk_manager.py`: Risk validation tests
- `test_portfolio_manager.py`: Portfolio calculations
- `test_gas_simulation.py`: Fee estimation tests
- `run_backtest.py`: Historical simulation
- `retrain_model.py`: Model retraining pipeline

---

### 2.9 **Documentation & Compliance**

- `README.md`: Quick start guide
- `governance_docs/protocol_whitepaper.md`: Technical architecture (14,000 word document)
- `governance_docs/smart_contract_architecture.md`: Contract design details
- `INTEGRATION_COMPLETE.md`: Integration status and methods
- `INTEGRATION_VERIFICATION.md`: Test verification guide
- `END_TO_END_INTEGRATION_GUIDE.md`: Setup instructions
- `CHANGES_SUMMARY.md`: Modification history
- `compliance/`: Regulatory documentation
  - `ethical_statement.md`
  - `regulatory_limitations.md`
  - `risk_disclosure.md`
  - `sebi_analysis.md` (India's Securities and Exchange Board regulations)

---

## 3. KEY FEATURES & FUNCTIONALITY

### 3.1 **Trade Execution**
✅ Manual execution via UI
✅ Automated execution based on AI signals
✅ Confidence-threshold filtering (minimum 0.65)
✅ 10-second cooldown between trades
✅ Buy/Sell/Hold decision logic
✅ Slippage simulation
✅ Gas fee simulation

### 3.2 **Risk Management**
✅ Position size limits
✅ Leverage caps (configurable)
✅ Liquidation triggers at 70% loss threshold
✅ Circuit breakers (±40% price movements)
✅ Portfolio-level drawdown protection
✅ Dynamic margin requirements

### 3.3 **Portfolio Tracking**
✅ Real-time cash balance
✅ Multi-position tracking
✅ Average cost basis calculation
✅ Profit/Loss per position
✅ Portfolio value evolution (history)
✅ Multi-user support with isolated wallets

### 3.4 **AI Signal Generation**
✅ Technical indicator computation (SMA, EMA, RSI, MACD)
✅ Confidence scoring (0-1 scale)
✅ Signal types: BUY, SELL, HOLD
✅ Mock prediction fallback
✅ Retraining on 30-day schedule
✅ Market data caching

### 3.5 **Blockchain Features**
✅ Immutable trade recording
✅ Smart contract enforcement
✅ Position tracking on-chain
✅ Gas simulation
✅ Multi-signature support
✅ Emergency pause mechanism

### 3.6 **Governance**
✅ Parameter proposal voting
✅ Confidence threshold adjustment
✅ Leverage limit changes
✅ Protocol fee governance
✅ Circuit breaker threshold tuning

### 3.7 **Analytics & Reporting**
✅ Real-time risk metrics
✅ Portfolio performance analytics
✅ Trade history audit trail
✅ User authentication/wallet recovery
✅ Dashboard visualizations

---

## 4. TECHNOLOGIES & TOOLS USED

### **Backend Stack**
| Component | Technology |
|-----------|------------|
| Core Platform | Python 3.12 |
| Web Framework | Streamlit |
| ML Libraries | scikit-learn, XGBoost, LightGBM, CatBoost |
| Technical Analysis | pandas-ta, TA-Lib |
| Data Processing | pandas, NumPy, SciPy |
| Model Training | scikit-learn RandomForestClassifier |
| Market Data | Yahoo Finance API, yfinance |
| API Framework | FastAPI, uvicorn |
| Database ORM | SQLAlchemy |
| Database | PostgreSQL (psycopg2) |
| Caching | Redis |
| HTTP Client | aiohttp, requests |

### **Blockchain Stack**
| Component | Technology |
|-----------|------------|
| Smart Contracts | Solidity 0.8.20 |
| Development Env | Hardhat (TypeScript) |
| Web3 Integration | web3.py |
| Ethereum Libs | eth-account, eth-abi, eth-utils |
| Contract Compilation | py-solc-x |
| Local Node | Hardhat node (simulates Ethereum) |
| Contract Types | TypeScript code generation |

### **Security & Crypto**
- **Encryption:** cryptography library
- **Key Management:** eth-account, Ethereum wallets
- **Hashing:** KECCAK-256 (Solidity built-in)
- **Signing:** ECDSA via eth-account

### **Data Science & Analysis**
- **ML Models:** Random Forest (200 estimators)
- **Hyperparameter Optimization:** Optuna, Hyperopt
- **Statistical Analysis:** statsmodels, scipy
- **Time Series:** arch (GARCH models for volatility)
- **Visualization:** Matplotlib, Seaborn, Plotly
- **Model Serialization:** joblib

### **Development & Testing**
- **Testing:** pytest
- **Type Checking:** Pylance (VS Code)
- **Environment:** Python virtual environment
- **Package Management:** pip, poetry support
- **Version Control:** Git
- **Logging:** Python logging module

### **Frontend**
- **UI Framework:** Streamlit
- **Auto-refresh:** streamlit-autorefresh
- **Charts:** Plotly (via Streamlit)
- **HTML/CSS:** st.markdown with custom CSS

---

## 5. DATA FLOW & ARCHITECTURE

### 5.1 **Complete System Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                   DAPPTRADE ECOSYSTEM                       │
└─────────────────────────────────────────────────────────────┘

1. DATA INGESTION LAYER
   ↓
   ├─ Market API (Yahoo Finance)
   │  └─ Raw OHLCV data [Open, High, Low, Close, Volume]
   │
   └─ NSE Adapter
      └─ Indian stock market data

2. FEATURE ENGINEERING LAYER
   ↓
   ├─ Technical Indicators
   │  ├─ SMA (14-period moving average)
   │  ├─ EMA (14-period exponential average)
   │  ├─ RSI (Relative Strength Index)
   │  ├─ MACD (Moving Average Convergence Divergence)
   │  └─ Volatility metrics
   │
   └─ Feature Pipeline
      └─ Normalized feature vectors

3. AI PREDICTION LAYER
   ↓
   ├─ Model Training (RandomForest)
   │  ├─ Historical feature data
   │  ├─ Binary target: Next-period return > 0?
   │  └─ 80/20 train/test split
   │
   └─ Prediction Engine
      ├─ Input: Latest features
      └─ Output: {signal: BUY|SELL|HOLD, confidence: 0.0-1.0}

4. SIGNAL FILTERING LAYER
   ↓
   ├─ Confidence Threshold Check (τ = 0.65)
   │  └─ If confidence < 0.65 → HOLD
   │
   └─ Price & Market Data
      └─ Current market price, timestamp

5. EXECUTION LAYER
   ↓
   ├─ Protocol Controller (Python)
   │  ├─ Simulation Mode (default)
   │  └─ Live Mode (blockchain)
   │
   ├─ Trade Validation
   │  ├─ Risk enforcement
   │  ├─ Leverage checks
   │  ├─ Position size limits
   │  └─ Circuit breaker evaluation
   │
   └─ Portfolio Update
      ├─ Update cash balance
      ├─ Update positions
      └─ Append to history

6. BLOCKCHAIN LAYER
   ↓
   ├─ Smart Contracts Execution
   │  ├─ TradingProtocol: Position management
   │  ├─ RiskManager: Validation
   │  ├─ PortfolioManager: Accounting
   │  ├─ Governance: Parameter updates
   │  └─ Ledger: Trade recording
   │
   ├─ Immutable Recording
   │  └─ Transaction hash, trade ID, PnL
   │
   └─ User Wallet Registry
      └─ Balance & position tracking

7. ANALYTICS LAYER
   ↓
   ├─ Portfolio History Analysis
   │  ├─ Daily returns calculation
   │  ├─ Risk metrics (Sharpe, Sortino, VaR, CVaR)
   │  ├─ Drawdown analysis
   │  └─ Risk classification
   │
   └─ Trade Ledger Analysis
      └─ Win rate, average PnL, frequency

8. UI LAYER
   ↓
   ├─ Streamlit Dashboard
   │  ├─ Real-time market prices
   │  ├─ AI signal display
   │  ├─ Portfolio summary
   │  ├─ Risk metrics cards
   │  ├─ Trade history table
   │  ├─ Governance voting interface
   │  └─ Blockchain explorer
   │
   └─ 10-second auto-refresh
```

### 5.2 **Trade Execution Flow**

```
User Initiates Trade (UI)
  ↓
[Step 1] AI Prediction
  ├─ Fetch latest market data (OHLCV)
  ├─ Compute technical indicators
  ├─ Run RandomForest model
  └─ Return: signal + confidence

[Step 2] Signal Validation
  ├─ Check confidence >= 0.65
  ├─ If below threshold → HOLD
  └─ Fetch current market price

[Step 3] Risk Enforcement
  ├─ Validate position size
  ├─ Check leverage
  ├─ Check collateral
  ├─ Check drawdown limits
  └─ Proceed only if all pass

[Step 4] Trade Execution
  ├─ SIMULATION MODE (default)
  │  ├─ Update portfolio_state["cash"]
  │  ├─ Update portfolio_state["positions"][stock]
  │  ├─ Calculate average cost basis
  │  └─ Append new value to history
  │
  └─ LIVE MODE (blockchain)
     ├─ Call TradingProtocol.openPosition()
     ├─ Contract validates risk
     ├─ Contract records on Ledger
     └─ Returns transaction hash

[Step 5] State Update
  ├─ Update user balance
  ├─ Update user positions
  ├─ Record transaction
  └─ Emit event to UI

[Step 6] UI Refresh
  └─ 10-second auto-refresh displays results
```

### 5.3 **Portfolio State Object**

```python
portfolio_state = {
    "cash": 9500.0,              # Remaining liquid capital
    "positions": {
        "RELIANCE.NS": {
            "quantity": 10,       # Holdings
            "price": 1500.0       # Average entry price
        },
        "TCS.NS": {
            "quantity": 5,
            "price": 3000.0
        }
    },
    "history": [
        10000.0,  # Day 1
        9500.0,   # Day 2
        9750.0,   # Day 3
        10200.0   # Day 4 (current)
    ]
}
```

### 5.4 **Governance Flow**

```
Governance Proposal
  ↓
User submits proposal:
  ├─ Parameter: "confidence_threshold"
  ├─ New value: 0.75
  └─ Duration: 7 days voting window

Voting Phase
  ├─ Other users vote FOR or AGAINST
  └─ Track votes

Execution
  ├─ After deadline, if votesFor > votesAgainst
  ├─ Call update_protocol_params()
  └─ New threshold applied to all future predictions
```

---

## 6. MAIN OUTPUTS & RESULTS

### 6.1 **Real-Time Outputs**

#### **Dashboard Metrics (Updated Every 10 Seconds)**

1. **Trading Metrics**
   - Current market price per stock
   - AI signal (BUY/SELL/HOLD)
   - Signal confidence (0-1 scale)
   - Position quantity held
   - Average entry price

2. **Portfolio Metrics**
   - Total cash balance
   - Current positions (symbol, qty, avg price)
   - Portfolio value snapshot
   - Total positions count

3. **Risk Metrics**
   - **Total Return %:** `(End_Value / Start_Value - 1) × 100`
   - **Sharpe Ratio:** `√252 × (μ_r - rf) / σ_r`
   - **Sortino Ratio:** `√252 × (μ_r - rf) / σ_downside`
   - **Max Drawdown %:** Peak-to-trough percentage decline
   - **VaR (95%):** 95th percentile loss
   - **CVaR (95%):** Expected shortfall beyond VaR
   - **Risk Classification:** High/Moderate/Low based on drawdown

4. **Trade History**
   - Symbol traded
   - Action (BUY/SELL)
   - Price at execution
   - Quantity
   - Timestamp
   - AI confidence
   - Status (SUCCESS/FAILED)

### 6.2 **Blockchain Outputs**

#### **Smart Contract Events**
```solidity
// TradingProtocol
event PositionOpened(uint256 id, address trader, uint256 price)
event PositionClosed(uint256 id, int256 pnl, uint256 price)
event PositionUpdated(uint256 id, uint256 newSize, uint256 price)

// Ledger
event TradeExecuted(uint256 id, address user, string symbol, bool isBuy, uint256 price, uint256 quantity, uint256 confidence)
event PositionUpdated(address user, string symbol, uint256 quantity, uint256 avgPrice)
event PnLUpdated(address user, int256 pnl)

// RiskManager
event RiskEvaluated(address user, uint256 riskScore)
event LiquidationTriggered(uint256 positionId)

// Governance
event ProposalCreated(uint256 id, string parameter, uint256 value)
event ProposalExecuted(uint256 id, string parameter, uint256 value)
event Voted(uint256 id, address voter, bool support)
```

#### **Immutable Records**
- Transaction hash
- Block number
- Trade ID
- User address
- Symbol
- Action (BUY/SELL)
- Price
- Quantity
- Timestamp
- AI confidence score
- PnL realized

### 6.3 **Logging Outputs**

#### **Log Files Generated**
```
logs/
├── ai.log          # AI model predictions and feature engineering
├── blockchain.log  # Smart contract interactions
├── transactions.log # Trade execution details
├── app.log         # General application events
└── LOG_STRUCTURE.py # Log schema definitions
```

#### **Example Log Entry**
```
2026-04-25 14:30:45,123 - INFO - 
TRADE_EXECUTED: user=0xabc..., symbol=RELIANCE.NS, 
action=BUY, price=1500.0, quantity=10, confidence=0.85,
status=SUCCESS, tx_hash=0x123...
```

### 6.4 **Test & Integration Results**

From `tests/integration_results.json`:
- **15+ integration tests**
- **0 failures**
- All systems connected (UI → Backend → Smart Contracts → Blockchain)
- ✅ AI predictions working
- ✅ Trade execution working
- ✅ Risk enforcement working
- ✅ Portfolio tracking working
- ✅ Governance functional
- ✅ Ledger recording verified

---

## 7. KEY FORMULAS & CALCULATIONS

### 7.1 **AI Prediction Formulas**

#### **Confidence Score Calculation**
```
RandomForest Confidence = P(Class=1) from all 200 trees
Range: [0, 1]
Decision: If confidence > 0.65 → execute signal
         Else → HOLD
```

#### **Technical Indicators**

1. **SMA (Simple Moving Average)**
   ```
   SMA_14 = Σ(Price[t-13:t]) / 14
   ```

2. **EMA (Exponential Moving Average)**
   ```
   EMA = Price[t] × α + EMA[t-1] × (1 - α)
   where α = 2 / (N + 1) = 2 / 15 ≈ 0.133
   ```

3. **RSI (Relative Strength Index)**
   ```
   RSI = 100 - (100 / (1 + RS))
   where RS = Average Gain / Average Loss (14-period)
   Range: [0, 100]
   ```

4. **MACD (Moving Average Convergence Divergence)**
   ```
   MACD = EMA_12 - EMA_26
   Signal = EMA_9(MACD)
   Histogram = MACD - Signal
   ```

---

### 7.2 **Portfolio Calculations**

#### **Equation 3.3: Portfolio Value & PnL**
```
Portfolio Value (V) = Σ (Quantity_i × Price_i) + Cash
where i = each open position

PnL = (Exit_Price - Entry_Price) × Quantity

For Long Position:
  PnL = (Current_Price - Entry_Price) × Quantity

For Short Position:
  PnL = (Entry_Price - Current_Price) × Quantity
```

#### **Average Cost Basis (Dollar-Cost Averaging)**
```
When adding to position:
  New_Avg_Price = (Old_Qty × Old_Price + New_Qty × New_Price) 
                  / (Old_Qty + New_Qty)
```

---

### 7.3 **Risk Metrics**

#### **Equation 3.4: Sharpe Ratio** (Risk-Adjusted Return)
```
Sharpe = (μ_returns - rf) / σ_returns × √252

where:
  μ_returns = mean daily return
  rf = risk-free rate (5% annual / 252 trading days)
  σ_returns = standard deviation of daily returns
  √252 = annualization factor

Interpretation:
  > 1.0 = Good
  > 2.0 = Very Good
  < 0.5 = Poor
```

#### **Sortino Ratio** (Downside Risk Only)
```
Sortino = (μ_returns - rf) / σ_downside × √252

where:
  σ_downside = std dev of negative returns only
  
Better than Sharpe for strategies with asymmetric risk
```

#### **Value at Risk (VaR) - 95% Confidence**
```
VaR(95%) = -Percentile(Daily Returns, 5)

Interpretation:
  95% chance that daily loss won't exceed VaR
  e.g., VaR = 2% → 95% chance loss ≤ 2% per day
```

#### **Conditional Value at Risk (CVaR)** - Expected Shortfall
```
CVaR(95%) = -Mean(Returns | Returns ≤ Percentile_5)

Interpretation:
  Average loss when loss exceeds VaR threshold
  Captures tail risk beyond VaR
```

#### **Maximum Drawdown**
```
Drawdown_t = (Peak_t - Value_t) / Peak_t × 100%

Max_Drawdown = min(Drawdown_t) over all time periods

Example:
  Peak portfolio value: $10,000
  Trough: $8,000
  Max Drawdown = (10,000 - 8,000) / 10,000 × 100% = 20%
```

---

### 7.4 **Risk Management Formulas**

#### **Position Leverage Calculation**
```
Leverage = Position_Size / Collateral

Max Allowed Leverage = 2x (configurable)

Trade blocked if: Leverage > Max_Leverage
```

#### **Liquidation Threshold (Equation 3.1)**
```
Liquidation_Price = Entry_Price × Liquidation_Threshold / 10000

Default Threshold = 70% (0.7 × Entry_Price)

Long position liquidated if: Price < Liquidation_Price
Short position liquidated if: Price > Liquidation_Price
```

#### **Circuit Breaker Condition (Equation 3.1)**
```
If Price > Reference_Price × 1.40 (40% spike)
  OR Price < Reference_Price × 0.60 (40% drop)
  → System paused, no new trades allowed

Prevents cascade failures in high volatility
```

---

### 7.5 **Execution Cost Model**

```
Total_Execution_Cost = Trade_Price × Quantity 
                      + Slippage 
                      + Gas_Fees 
                      + Protocol_Fee

Slippage = Entry_Price × 0.01 (1% default, configurable)

Gas_Fees = simulated on local blockchain

Protocol_Fee = variable per governance vote
```

---

### 7.6 **Model Training Formulas**

#### **Classification Target**
```
y_t = 1 if (Price[t+1] / Price[t]) > 1  (BUY signal)
    = 0 if (Price[t+1] / Price[t]) ≤ 1  (SELL/HOLD signal)
```

#### **RandomForest Decision**
```
For each sample:
  1. All 200 trees vote: BUY or SELL
  2. Confidence = count(BUY votes) / 200
  3. Prediction = argmax(BUY, SELL confidence)

Feature Importance ranked by:
  - Mean decrease in impurity (Gini)
  - Top features: SMA, EMA, RSI, MACD, volatility
```

#### **Cross-Validation**
```
K-Fold CV (default k=5):
  1. Split data into 5 equal folds
  2. Train on 4 folds, test on 1
  3. Repeat 5 times
  4. Average accuracy = overall model performance
```

---

## 8. SYSTEM CONSTRAINTS & PARAMETERS

### 8.1 **Trading Parameters**

| Parameter | Value | Configurable |
|-----------|-------|--------------|
| Initial Capital | 10,000 ETH | ✅ |
| Confidence Threshold | 0.65 | ✅ |
| Min Trade Size | 1 unit | ✅ |
| Max Position Size | 100 units | ✅ |
| Leverage Limit | 2x | ✅ |
| Slippage | 1% | ✅ |
| Trade Cooldown | 10 seconds | ✅ |
| Auto-refresh Interval | 10 seconds | ✅ |

### 8.2 **Risk Parameters**

| Parameter | Value | Configurable |
|-----------|-------|--------------|
| Liquidation Threshold | 70% loss | ✅ |
| Circuit Breaker | ±40% price move | ✅ |
| Max Drawdown Alert | >40% | ✅ |
| Risk-Free Rate | 5% annual | ✅ |

### 8.3 **Data Parameters**

| Parameter | Value |
|-----------|-------|
| Market Data Interval | 1-minute or 1-day |
| Data Lookback | 6 months historical |
| Technical Indicator Window | 14-period |
| Model Retraining | Every 30 days |
| Rate Limiting | 0.2s between API calls |

### 8.4 **Blockchain Parameters**

| Parameter | Value |
|-----------|-------|
| Gas Limit | 3,000,000 |
| Network | Hardhat (local) or Ethereum-compatible |
| Solidity Version | 0.8.20 |
| Position Storage | Mapping by ID |

---

## 9. DEPLOYMENT & INFRASTRUCTURE

### 9.1 **Local Development Setup**

```bash
# Terminal 1: Start Hardhat local blockchain
npx hardhat node

# Terminal 2: Deploy smart contracts
npx hardhat run scripts/deploy.js --network localhost

# Terminal 3: Run integration tests
python scripts/integration_test.py

# Terminal 4: Start Streamlit UI
streamlit run app.py
```

### 9.2 **Environment Variables** (`.env`)
```
WEB3_PROVIDER_URI=http://127.0.0.1:8545
PRIVATE_KEY=<deployer-private-key>
ACCOUNT_ADDRESS=<deployer-address>
ENCRYPTION_SECRET=<secret-key>
```

### 9.3 **Docker Support**
```
docker-compose up  # Brings up Ganache test blockchain
```

---

## 10. PROJECT STATISTICS

| Metric | Count |
|--------|-------|
| Smart Contracts | 10 |
| Python Modules | 20+ |
| UI Pages | 7 |
| Technical Indicators | 4+ |
| Risk Metrics | 6+ |
| Trading Modes | 2 (simulation, live) |
| Supported Stocks | 5+ |
| Integration Tests | 15+ |
| Log Files | 4 |
| Total Supported Currencies | 1 (simulated ETH) |

---

## 11. KEY ARCHITECTURAL PATTERNS

### 11.1 **Design Patterns Used**

1. **Separation of Concerns**
   - AI logic separate from blockchain logic
   - UI separate from backend
   - Data ingestion separate from prediction

2. **Factory Pattern**
   - ContractLoader instantiates contracts
   - MarketAPIClient creates data connections

3. **Strategy Pattern**
   - Multiple execution strategies (simulation vs live)
   - Multiple risk validation strategies

4. **Observer Pattern**
   - Streamlit auto-refresh listening for state changes
   - Smart contract events triggering UI updates

5. **Repository Pattern**
   - UserWalletRegistry abstracts user storage
   - Ledger abstracts trade history storage

### 11.2 **Error Handling**

- Graceful fallback to simulation mode if blockchain unavailable
- Mock data generation if ML model unavailable
- Safe normalization of portfolio data
- Transaction validation before submission
- Circuit breaker triggers on anomalies

---

## 12. COMPLIANCE & REGULATORY FEATURES

- **SEBI Simulation:** India's Securities and Exchange Board regulations
- **Risk Disclosure:** Full risk warnings in UI
- **Ethical Statement:** Clearly documented in compliance folder
- **Regulatory Limitations:** Explicitly stated constraints
- **Simulation Notice:** Clear distinction between demo and real trading

---

## 13. FUTURE EXTENSIONS (DOCUMENTED)

- Multi-chain execution
- Cross-chain liquidity routing
- On-chain model inference (ZKML)
- Decentralized data feeds
- Autonomous treasury management
- Token-based DAO governance
- Staking for signal providers

---

## CONCLUSION

**DAPPTRADE** is a sophisticated hybrid trading platform combining:
- **Intelligent AI** for signal generation with confidence scoring
- **Verifiable Blockchain** for immutable trade execution
- **Robust Risk Management** preventing harmful trades
- **Transparent Analytics** for real-time performance monitoring
- **Decentralized Governance** for community parameter tuning

The system demonstrates academic contributions in:
- Hybrid AI-Oracle-Blockchain architecture
- Decentralized enforcement of trading logic
- Simulation of regulatory compliance
- Transparent execution and governance

**Status:** ✅ Fully integrated and operational with 15+ passing tests.
