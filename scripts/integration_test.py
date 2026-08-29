#!/usr/bin/env python3
"""
integration_test.py
===================
End-to-end integration test for DAPPTRADE system.

Tests connectivity between:
- Python backend
- Smart Contracts
- Blockchain Node
- Ledger synchronization
- Risk metrics calculation
"""

import sys
import os
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import AppConfig
from blockchain_protocol.web3_layer.web3_provider import get_web3_connection
from blockchain_protocol.web3_layer.contract_loader import ContractLoader
from blockchain_protocol.execution_engine.protocol_controller import ProtocolController
from blockchain_protocol.storage.user_wallet_registry import UserWalletRegistry


class IntegrationTester:
    """Test end-to-end system connectivity"""

    def __init__(self):
        self.config = AppConfig()
        self.web3 = None
        self.protocol = None
        self.registry = UserWalletRegistry()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "passed": 0,
            "failed": 0
        }

    def log_test(self, name: str, passed: bool, message: str = ""):
        """Log a test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} | {name}")
        if message:
            print(f"    └─ {message}")
        
        self.results["tests"][name] = {
            "passed": passed,
            "message": message
        }
        
        if passed:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1

    # ===================================================
    # TEST 1: WEB3 CONNECTION
    # ===================================================
    def test_web3_connection(self):
        """Test blockchain node connectivity"""
        print("\n[TEST 1] Web3 Provider Connection")
        print("-" * 60)
        
        try:
            self.web3 = get_web3_connection()
            
            if not self.web3.is_connected():
                self.log_test(
                    "Web3 Connection",
                    False,
                    "Could not connect to blockchain node. Is hardhat running?"
                )
                return False
            
            # Get network info
            chain_id = self.web3.eth.chain_id
            block = self.web3.eth.block_number
            
            self.log_test(
                "Web3 Connection",
                True,
                f"Connected to chain {chain_id}, block {block}"
            )
            
            # Test account access
            accounts = self.web3.eth.accounts
            if accounts:
                self.log_test(
                    "Account Access",
                    True,
                    f"Found {len(accounts)} accounts"
                )
            
            return True
            
        except Exception as e:
            self.log_test("Web3 Connection", False, str(e))
            return False

    # ===================================================
    # TEST 2: CONTRACT LOADER
    # ===================================================
    def test_contract_loader(self):
        """Test contract loading"""
        print("\n[TEST 2] Contract Loader")
        print("-" * 60)
        
        if not self.web3:
            self.log_test("Contract Loader", False, "Web3 not connected")
            return False
        
        try:
            loader = ContractLoader(self.web3)
            addresses = loader.load_addresses()
            
            required_contracts = [
                "TradingProtocol",
                "Ledger",
                "Governance",
                "PortfolioManager"
            ]
            
            missing = [c for c in required_contracts if c not in addresses]
            
            if missing:
                self.log_test(
                    "Contract Addresses",
                    False,
                    f"Missing addresses: {missing}"
                )
                return False
            
            self.log_test(
                "Contract Addresses",
                True,
                f"All {len(required_contracts)} contracts found"
            )
            
            # Try loading contracts
            for contract_name in required_contracts:
                try:
                    contract = loader.get_contract(contract_name)
                    self.log_test(
                        f"Load {contract_name}",
                        True,
                        f"Loaded with ABI ({len(contract.abi)} methods)"
                    )
                except Exception as e:
                    self.log_test(
                        f"Load {contract_name}",
                        False,
                        str(e)
                    )
            
            return True
            
        except Exception as e:
            self.log_test("Contract Loader", False, str(e))
            return False

    # ===================================================
    # TEST 3: PROTOCOL CONTROLLER
    # ===================================================
    def test_protocol_controller(self):
        """Test ProtocolController initialization"""
        print("\n[TEST 3] Protocol Controller")
        print("-" * 60)
        
        try:
            self.protocol = ProtocolController(self.config, self.web3)
            
            # Check initial state
            state = self.protocol.get_portfolio_state()
            
            has_cash = "cash" in state and state["cash"] > 0
            has_history = "history" in state and isinstance(state["history"], list)
            has_positions = "positions" in state and isinstance(state["positions"], dict)
            
            self.log_test(
                "Portfolio State Structure",
                has_cash and has_history and has_positions,
                f"Cash: {state.get('cash', 0)}, History: {len(state.get('history', []))}, Positions: {len(state.get('positions', {}))}"
            )
            
            # Check parameters
            params = self.protocol.get_protocol_parameters()
            self.log_test(
                "Protocol Parameters",
                bool(params),
                f"Loaded {len(params)} parameters"
            )
            
            # Check enforce_rules method exists
            rules = self.protocol.enforce_rules("0x123", "RELIANCE.NS", "BUY", 10)
            self.log_test(
                "Enforce Rules Method",
                "approved" in rules,
                f"Rules check: {rules.get('reason', 'OK')}"
            )
            
            return True
            
        except Exception as e:
            self.log_test("Protocol Controller", False, str(e))
            return False

    # ===================================================
    # TEST 4: SIMULATION TRADE
    # ===================================================
    def test_simulation_trade(self):
        """Test trade execution in simulation mode"""
        print("\n[TEST 4] Trade Execution (Simulation)")
        print("-" * 60)
        
        if not self.protocol:
            self.log_test("Simulation Trade", False, "Protocol not initialized")
            return False
        
        try:
            # 🔥 FIX: Use affordable quantities (6 * 1000 = 6000 < 10000 initial capital)
            signal = {
                "stock": "RELIANCE.NS",
                "signal": "BUY",
                "confidence": 0.85,
                "price": 1000.0,  # Changed from 1500.0
                "quantity": 6,     # Changed from 10
                "user": "test_user"
            }
            
            result = self.protocol.execute_trade(signal)
            
            success = result.get("status") == "SIMULATED"
            self.log_test(
                "Execute BUY Trade",
                success,
                f"Result: {result.get('status', 'FAILED')} | Cost: 6000, Cash: {self.protocol.portfolio_state['cash']}"
            )
            
            # Check portfolio state updated
            state = self.protocol.get_portfolio_state()
            has_position = "RELIANCE.NS" in state["positions"]
            has_history = len(state["history"]) > 1
            
            self.log_test(
                "Portfolio Updated",
                has_position and has_history,
                f"Position: {has_position}, History entries: {len(state['history'])}"
            )
            
            # Execute SELL trade - sell 3 shares at 1010
            signal_sell = {
                "stock": "RELIANCE.NS",
                "signal": "SELL",
                "confidence": 0.80,
                "price": 1010.0,  # Changed from 1510.0
                "quantity": 3,     # Changed from 5 (can't sell more than we have)
                "user": "test_user"
            }
            
            result_sell = self.protocol.execute_trade(signal_sell)
            success_sell = result_sell.get("status") == "SIMULATED"
            
            self.log_test(
                "Execute SELL Trade",
                success_sell,
                f"Result: {result_sell.get('status', 'FAILED')} | Proceeds: 3030"
            )
            
            return True
            
        except Exception as e:
            self.log_test("Simulation Trade", False, str(e))
            return False

    # ===================================================
    # TEST 5: RISK METRICS
    # ===================================================
    def test_risk_metrics(self):
        """Test risk metrics calculation"""
        print("\n[TEST 5] Risk Metrics Calculation")
        print("-" * 60)
        
        if not self.protocol:
            self.log_test("Risk Metrics", False, "Protocol not initialized")
            return False
        
        try:
            state = self.protocol.get_portfolio_state()
            history = state.get("history", [])
            
            if len(history) < 2:
                self.log_test(
                    "Portfolio History",
                    False,
                    f"Need at least 2 data points, have {len(history)}"
                )
                return False
            
            self.log_test(
                "Portfolio History",
                True,
                f"Have {len(history)} history points"
            )
            
            # Test PnL calculation
            pnl = self.protocol._calculate_pnl()
            self.log_test(
                "PnL Calculation",
                isinstance(pnl, (int, float)),
                f"PnL: {pnl:.2f}"
            )
            
            return True
            
        except Exception as e:
            self.log_test("Risk Metrics", False, str(e))
            return False

    # ===================================================
    # TEST 6: USER REGISTRY
    # ===================================================
    def test_user_registry(self):
        """Test user registration and authentication"""
        print("\n[TEST 6] User Registry")
        print("-" * 60)
        
        try:
            # Create test user
            username = f"test_user_{int(datetime.now().timestamp())}"
            password = "test_password_123"
            
            user = self.registry.create_user(username, password)
            
            has_wallet = "wallet_address" in user
            has_key = "private_key" in user
            
            self.log_test(
                "Create User",
                has_wallet and has_key,
                f"Wallet: {user.get('wallet_address', 'N/A')[:10]}..."
            )
            
            # Test authentication
            auth = self.registry.authenticate_user(username, password)
            self.log_test(
                "Authenticate User",
                auth is not None,
                f"Auth result: {'OK' if auth else 'FAILED'}"
            )
            
            # Test wallet access
            wallet = self.registry.get_wallet(username)
            self.log_test(
                "Get Wallet",
                wallet is not None,
                f"Wallet: {wallet[:10] if wallet else 'N/A'}..."
            )
            
            return True
            
        except Exception as e:
            self.log_test("User Registry", False, str(e))
            return False

    # ===================================================
    # TEST 7: GOVERNANCE
    # ===================================================
    def test_governance(self):
        """Test governance proposal"""
        print("\n[TEST 7] Governance")
        print("-" * 60)
        
        if not self.protocol:
            self.log_test("Governance", False, "Protocol not initialized")
            return False
        
        try:
            # Propose parameter change
            result = self.protocol.propose_change("risk_limit", 0.75)
            
            success = result and (result.startswith("0x") or result.startswith("0xproposal"))
            self.log_test(
                "Propose Change",
                success,
                f"Proposal ID: {result[:30] if result else 'N/A'}..."
            )
            
            # Check parameter was updated (in simulation mode)
            params = self.protocol.get_protocol_parameters()
            updated = params.get("risk_limit") == 0.75
            
            self.log_test(
                "Parameter Updated",
                updated,
                f"risk_limit: {params.get('risk_limit', 'N/A')}"
            )
            
            return True
            
        except Exception as e:
            self.log_test("Governance", False, str(e))
            return False

    # ===================================================
    # MAIN TEST RUNNER
    # ===================================================
    def run_all_tests(self):
        """Run all integration tests"""
        print("=" * 60)
        print("DAPPTRADE SYSTEM INTEGRATION TEST")
        print("=" * 60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run tests in order
        self.test_web3_connection()
        self.test_contract_loader()
        self.test_protocol_controller()
        self.test_simulation_trade()
        self.test_risk_metrics()
        self.test_user_registry()
        self.test_governance()
        
        # Print summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        total = self.results['passed'] + self.results['failed']
        if total > 0:
            percentage = (self.results['passed'] / total) * 100
            print(f"Success Rate: {percentage:.1f}%")
        print("=" * 60)
        
        # Save results
        with open("tests/integration_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        print("\n📊 Results saved to tests/integration_results.json")
        
        return self.results['failed'] == 0


def main():
    """Main entry point"""
    tester = IntegrationTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
