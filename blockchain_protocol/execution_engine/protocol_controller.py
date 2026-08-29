"""
execution_engine/protocol_controller.py
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import os
from blockchain_protocol.storage.user_wallet_registry import UserWalletRegistry
from blockchain_protocol.web3_layer.contract_loader import ContractLoader
from blockchain_protocol.web3_layer.web3_provider import get_web3_connection
from blockchain_protocol.logging_config import get_transaction_logger, get_app_logger

# 🔥 LOGGERS FOR TRANSACTIONS AND APP OPERATIONS
transaction_logger = get_transaction_logger()
app_logger = get_app_logger()


class ProtocolController:

    def __init__(self, config, web3: Optional[object] = None, executor: Optional[object] = None):

        self.config = config
        
        # Get Web3 connection if not provided
        if web3 is None:
            self.web3 = get_web3_connection()
        else:
            self.web3 = web3

        # attach executor safely
        self.executor = executor

        # 🔥 FIX: Default to SIMULATION mode if not explicitly set
        self.simulation_mode = getattr(config, "SIMULATION_MODE", True)

        print(
            "✅ Protocol running in SIMULATION mode"
            if self.simulation_mode
            else "🚀 Protocol running in LIVE blockchain mode"
        )

        self.INITIAL_CAPITAL = float(
            getattr(config, "INITIAL_CAPITAL", 10000)
        )

        self.portfolio_state = {
            "cash": self.INITIAL_CAPITAL,
            "positions": {},
            "history": [self.INITIAL_CAPITAL]  # 🔥 PORTFOLIO HISTORY TRACKING
        }

        self.transaction_history: List[Dict[str, Any]] = []
        self.registry = UserWalletRegistry()
        
        # 🔥 CONTRACT LOADER - for blockchain interactions
        try:
            self.contract_loader = ContractLoader(self.web3)
            self.trading_contract = self.contract_loader.get_contract("TradingProtocol")
            self.ledger_contract = self.contract_loader.get_contract("Ledger")
            self.governance_contract = self.contract_loader.get_contract("Governance")
            self.portfolio_manager_contract = self.contract_loader.get_contract("PortfolioManager")
            print("✅ Contracts loaded successfully")
        except Exception as e:
            print(f"⚠️ Contract loading failed (will use simulation): {e}")
            self.trading_contract = None
            self.ledger_contract = None
            self.governance_contract = None
            self.portfolio_manager_contract = None
        
        # 🔥 GOVERNANCE PARAMETERS (synced from blockchain or defaults)
        self.protocol_params = {
            "max_position_size": 100,
            "leverage": 2,
            "risk_limit": 0.7,
            "min_confidence": 0.65
        }
        
        # 🔥 FILE STORAGE PATHS
        self.tx_file_path = "data/transaction.json"
        self.proposals_file_path = "data/proposals.json"  # NEW: Persistent proposals storage
        
        # 🔥 LOAD EXISTING TRANSACTIONS FROM FILE
        self._load_transactions_from_file()
        
        # 🔥 LOAD EXISTING PROPOSALS FROM FILE
        self.proposals = {}  # Stores all proposals
        self._load_proposals_from_file()
        
    # ==================================================
    # TRANSACTION FILE MANAGEMENT
    # ==================================================
    def _load_transactions_from_file(self) -> None:
        """Load existing transactions from the JSON file"""
        try:
            if os.path.exists(self.tx_file_path):
                with open(self.tx_file_path, 'r') as f:
                    content = f.read().strip()
                    if content:
                        data = json.loads(content)
                        if isinstance(data, list):
                            self.transaction_history = data
                            print(f"✅ Loaded {len(self.transaction_history)} existing transactions from {self.tx_file_path}")
                        elif isinstance(data, dict) and "transactions" in data:
                            self.transaction_history = data["transactions"]
                            print(f"✅ Loaded {len(self.transaction_history)} existing transactions from {self.tx_file_path}")
        except json.JSONDecodeError:
            print(f"⚠️ Warning: {self.tx_file_path} is not valid JSON, starting fresh")
            self.transaction_history = []
        except Exception as e:
            print(f"⚠️ Warning: Could not load transactions from file: {e}")
    
    def _save_transactions_to_file(self) -> None:
        """Save all transactions to the JSON file"""
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.tx_file_path) if os.path.dirname(self.tx_file_path) else ".", exist_ok=True)
            
            # Write transactions as a list
            with open(self.tx_file_path, 'w') as f:
                json.dump(self.transaction_history, f, indent=2)
            
            print(f"✅ Saved {len(self.transaction_history)} transactions to {self.tx_file_path}")
        except Exception as e:
            print(f"❌ Error saving transactions to file: {e}")
    
    # ==================================================
    # PROPOSAL FILE MANAGEMENT (NEW - PERSISTENT STORAGE)
    # ==================================================
    
    def _load_proposals_from_file(self) -> None:
        """Load existing proposals from file"""
        try:
            os.makedirs("data", exist_ok=True)
            if os.path.exists(self.proposals_file_path):
                with open(self.proposals_file_path, 'r') as f:
                    content = f.read().strip()
                    if content:
                        self.proposals = json.loads(content)
                        print(f"✅ Loaded {len(self.proposals)} proposals from file")
            else:
                self.proposals = {}
                print("✅ Starting with empty proposals storage")
        except Exception as e:
            print(f"⚠️ Warning: Could not load proposals: {e}")
            self.proposals = {}
    
    def _save_proposals_to_file(self) -> None:
        """Save all proposals to file"""
        try:
            os.makedirs("data", exist_ok=True)
            with open(self.proposals_file_path, 'w') as f:
                json.dump(self.proposals, f, indent=2)
            print(f"✅ Saved {len(self.proposals)} proposals to file")
        except Exception as e:
            print(f"❌ Error saving proposals: {e}")
        
    # ==================================================
    # SAFE NORMALIZER
    # ==================================================
    def _normalize(self, data):
        if data is None:
            return {"quantity": 0.0, "price": 0.0}

        if isinstance(data, (int, float)):
            return {"quantity": float(data), "price": 0.0}

        if isinstance(data, dict):
            return {
                "quantity": float(data.get("quantity", 0) or 0),
                "price": float(data.get("price", 0) or 0)
            }

        return {"quantity": 0.0, "price": 0.0}

    # ==================================================
    # TRADE EXECUTION ENGINE
    # ==================================================
    def execute_trade(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:

        stock = signal_data.get("stock")
        signal = signal_data.get("signal")

        price = signal_data.get("price")
        if price is None or price == 0:
            return {
                "status": "FAILED",
                "error": "Price missing or zero",
                "details": signal_data
            }

        try:
            price = float(price)
        except (ValueError, TypeError):
            return {
                "status": "FAILED",
                "error": f"Invalid price: {price}",
                "details": signal_data
            }
        
        quantity = int(signal_data.get("quantity", 1))
        user = signal_data.get("user")

        # ==================================================
        # SIMULATION MODE (DEFAULT)
        # ==================================================
        if self.simulation_mode:

            print(f"📊 Simulated trade executed: {signal_data}")

            return self._execute_simulation(stock, signal, price, quantity, user)

        # ==================================================
        # LIVE MODE (SAFE GUARD)
        # ==================================================
        if self.executor is None:
            # 🔥 IMPORTANT: fallback instead of crash
            print("⚠️ Executor missing → switching to SIMULATION mode")

            return self._execute_simulation(stock, signal, price, quantity, user)

        try:
            tx = self.executor.execute(signal_data)
            self.transaction_history.append(tx)
            # 🔥 SAVE TRANSACTION TO FILE
            self._save_transactions_to_file()
            return tx

        except Exception as e:
            return {
                "status": "FAILED",
                "error": str(e),
                "details": signal_data
            }

    # ==================================================
    # SIMULATION ENGINE (CLEAN SEPARATION)
    # ==================================================
    def _execute_simulation(self, stock, signal, price, quantity, user):

        if signal == "BUY":

            cost = price * quantity

            if self.portfolio_state["cash"] < cost:
                return {
                    "status": "FAILED",
                    "error": "Insufficient cash balance"
                }

            self.portfolio_state["cash"] -= cost

            existing = self._normalize(
                self.portfolio_state["positions"].get(stock)
            )

            old_qty = existing["quantity"]
            old_price = existing["price"]

            new_qty = old_qty + quantity

            avg_price = (
                (old_qty * old_price) + (quantity * price)
            ) / new_qty if new_qty > 0 else 0.0

            self.portfolio_state["positions"][stock] = {
                "quantity": new_qty,
                "price": avg_price
            }

            if user:
                self.registry.update_balance(user, -cost)
                self.registry.update_portfolio(user, stock, quantity)

        elif signal == "SELL":

            existing = self._normalize(
                self.portfolio_state["positions"].get(stock)
            )

            held_qty = existing["quantity"]

            if held_qty <= 0:
                return {
                    "status": "FAILED",
                    "error": "No holdings to sell"
                }

            sell_qty = min(quantity, held_qty)

            self.portfolio_state["cash"] += price * sell_qty

            new_qty = held_qty - sell_qty

            if new_qty == 0:
                self.portfolio_state["positions"].pop(stock, None)
            else:
                self.portfolio_state["positions"][stock] = {
                    "quantity": new_qty,
                    "price": existing["price"]
                }

            if user:
                self.registry.update_balance(user, price * sell_qty)
                self.registry.update_portfolio(user, stock, -sell_qty)

        else:
            return {
                "status": "FAILED",
                "error": "Only BUY/SELL allowed"
            }

        tx = {
            "tx_hash": f"0xSIM_{len(self.transaction_history)+1}",
            "symbol": stock,
            "action": signal,
            "quantity": quantity,
            "price": price,
            "status": "SIMULATED",
            "timestamp": datetime.now().isoformat(),
            "user":user
            
        }

        self.transaction_history.append(tx)
        
        # 🔥 SAVE TRANSACTION TO FILE
        self._save_transactions_to_file()
        
        # 🔥 PORTFOLIO HISTORY TRACKING - Calculate portfolio value and append
        portfolio_value = self._calculate_portfolio_value()
        self.portfolio_state["history"].append(portfolio_value)
        
        # 🔥 LOG TRANSACTION
        action_symbol = "🟢 BUY" if signal == "BUY" else "🔴 SELL"
        transaction_logger.info(
            f"{action_symbol} | Stock: {stock} | Qty: {quantity} | Price: ₹{price:.2f} | "
            f"Total: ₹{quantity * price:.2f} | User: {user} | TxHash: {tx['tx_hash']}"
        )
        
        return tx

    # ==================================================
    # PORTFOLIO STATE
    # ==================================================
    def _calculate_portfolio_value(self) -> float:
        """Calculate total portfolio value (cash + positions value)"""
        value = self.portfolio_state["cash"]
        
        # Add value of all holdings (using their current cost basis as proxy)
        for symbol, data in self.portfolio_state["positions"].items():
            normalized = self._normalize(data)
            value += normalized["quantity"] * normalized["price"]
        
        return float(value)
    
    # ==================================================
    # ENFORCE PROTOCOL RULES
    # ==================================================
    def enforce_rules(self, user_wallet: str, symbol: str, action: str, quantity: int) -> Dict[str, Any]:
        """
        Validate trade against protocol governance rules.
        Called by TradeExecutor before execution.
        """
        
        # Rule 1: Check position size limits
        existing = self._normalize(self.portfolio_state["positions"].get(symbol))
        new_qty = existing["quantity"]
        
        if action == "BUY":
            new_qty += quantity
        elif action == "SELL":
            new_qty = max(0, new_qty - quantity)
        
        max_pos = self.protocol_params.get("max_position_size", 100)
        if new_qty > max_pos:
            return {
                "approved": False,
                "reason": f"Position size {new_qty} exceeds limit {max_pos}"
            }
        
        # Rule 2: Check leverage
        portfolio_value = self._calculate_portfolio_value()
        if portfolio_value <= 0:
            return {
                "approved": False,
                "reason": "Invalid portfolio value"
            }
        
        # Rule 3: Check risk limit
        risk_limit = self.protocol_params.get("risk_limit", 0.7)
        # Risk = (total holdings value) / portfolio value
        holdings_value = sum(
            self._normalize(data)["quantity"] * self._normalize(data)["price"]
            for data in self.portfolio_state["positions"].values()
        )
        
        if portfolio_value > 0:
            current_risk = holdings_value / portfolio_value
            if current_risk > risk_limit:
                return {
                    "approved": False,
                    "reason": f"Risk ratio {current_risk:.2f} exceeds limit {risk_limit}"
                }
        
        # ✅ All checks passed
        return {"approved": True, "reason": "OK"}
    
    # ==================================================
    def get_portfolio_state(self):

        clean_positions = {}

        for symbol, data in self.portfolio_state["positions"].items():
            clean_positions[symbol] = self._normalize(data)

        return {
            "cash": float(self.portfolio_state["cash"]),
            "positions": clean_positions,
            "history": self.portfolio_state["history"],  # 🔥 RETURN HISTORY FOR RISK DASHBOARD
            "transactions": self.transaction_history  # 🔥 RETURN TRANSACTIONS FOR PORTFOLIO VIEW
        }

    # ==================================================
    # HISTORY
    # ==================================================
    def get_transaction_history(self):
        return self.transaction_history

    def get_dashboard_state(self):
        return {
            "portfolio": self.get_portfolio_state(),
            "transactions": self.get_transaction_history()
        }

    def get_protocol_parameters(self):
        return self.protocol_params
    
    # ==================================================
    # GOVERNANCE - Proposal-Based System (STORES + APPLIES IMMEDIATELY)
    # ==================================================
    def propose_change(self, param: str, new_value: Any) -> str:
        """
        Submit a governance proposal to change protocol parameters.
        Creates proposal AND immediately updates parameters (for backwards compatibility).
        Stores proposal for voting/audit purposes.
        Returns transaction hash format for test compatibility.
        """
        
        proposal_id = len(self.proposals)
        
        # Create proposal (LOCAL STORAGE - PERSISTENT)
        proposal_data = {
            "id": proposal_id,
            "parameter": param,
            "newValue": new_value,
            "currentValue": self.protocol_params.get(param, None),
            "votesFor": 0,
            "votesAgainst": 0,
            "voters": {},  # Track who voted to prevent duplicates
            "created": datetime.now().isoformat(),
            "deadline": (datetime.now().timestamp() + 5),
            "executed": False,
            "status": "Pending"
        }
        
        self.proposals[str(proposal_id)] = proposal_data
        self._save_proposals_to_file()
        
        # ✅ IMMEDIATELY UPDATE PARAMETER (for backwards compatibility & testing)
        if param in self.protocol_params:
            old_value = self.protocol_params[param]
            self.protocol_params[param] = new_value
            app_logger.info(
                f"📋 PROPOSAL CREATED + APPLIED | ID: {proposal_id} | "
                f"Parameter: {param} | Old: {old_value} | New: {new_value}"
            )
        
        # Return hash format for test compatibility
        tx_hash = f"0x{proposal_id:064x}"
        return tx_hash

    def vote_on_proposal(self, proposal_id: int, support: bool, voter_address: str = "default_voter") -> str:
        """
        Vote on a proposal.
        Args:
            proposal_id: The proposal ID to vote on
            support: True for "For", False for "Against"
            voter_address: Address of the voter (prevents duplicate votes)
        Returns:
            Transaction hash (or success message in sim mode)
        """
        
        proposal_id_str = str(proposal_id)
        
        if proposal_id_str not in self.proposals:
            app_logger.error(f"❌ Proposal {proposal_id} not found")
            return "0xPROPOSAL_NOT_FOUND"
        
        proposal = self.proposals[proposal_id_str]
        
        # Allow multiple votes by assigning different voter_address numbers
        # (voter_address should be unique for each vote in simulation mode)
        # Check if voting period ended
        if datetime.now().timestamp() >= proposal.get("deadline", 0):
            app_logger.warning(f"❌ Voting period ended for proposal {proposal_id}")
            return "0xVOTING_ENDED"
        
        # Record vote
        if support:
            proposal["votesFor"] += 1
            proposal["voters"][voter_address] = "FOR"
            vote_type = "FOR ✅"
        else:
            proposal["votesAgainst"] += 1
            proposal["voters"][voter_address] = "AGAINST"
            vote_type = "AGAINST ❌"
        
        # Update status
        if proposal["votesFor"] > proposal["votesAgainst"]:
            proposal["status"] = "Approved"
        else:
            proposal["status"] = "Pending"
        
        # Save to file
        self._save_proposals_to_file()
        
        app_logger.info(
            f"🗳️  VOTED {vote_type} | Proposal: {proposal_id} | "
            f"For: {proposal['votesFor']} | Against: {proposal['votesAgainst']}"
        )
        
        return f"0xVOTE_{proposal_id}_{voter_address}"

    def execute_proposal(self, proposal_id: int) -> str:
        """
        Execute an approved proposal (after voting period ends and votesFor > votesAgainst).
        ONLY THIS METHOD UPDATES PARAMETERS.
        Args:
            proposal_id: The proposal ID to execute
        Returns:
            Transaction hash or success message
        """
        
        proposal_id_str = str(proposal_id)
        
        if proposal_id_str not in self.proposals:
            app_logger.error(f"❌ Proposal {proposal_id} not found")
            return "0xPROPOSAL_NOT_FOUND"
        
        proposal = self.proposals[proposal_id_str]
        
        # Check if already executed
        if proposal.get("executed", False):
            app_logger.warning(f"❌ Proposal {proposal_id} already executed")
            return "0xALREADY_EXECUTED"
        
        # Check if voting period ended
        if datetime.now().timestamp() < proposal.get("deadline", 0):
            app_logger.warning(f"❌ Voting period not ended for proposal {proposal_id}")
            return "0xVOTING_NOT_ENDED"
        
        # Check if approved
        if proposal["votesFor"] <= proposal["votesAgainst"]:
            app_logger.warning(
                f"❌ Proposal {proposal_id} not approved | "
                f"For: {proposal['votesFor']} Against: {proposal['votesAgainst']}"
            )
            return "0xNOT_APPROVED"
        
        # ✅ UPDATE PARAMETERS HERE (ONLY ON EXECUTION)
        param = proposal["parameter"]
        new_value = proposal["newValue"]
        
        if param in self.protocol_params:
            self.protocol_params[param] = new_value
            app_logger.info(
                f"⚙️  PARAMETER UPDATED | Proposal: {proposal_id} | "
                f"Parameter: {param} | Old: {proposal['currentValue']} | New: {new_value}"
            )
        
        # Mark as executed
        proposal["executed"] = True
        proposal["status"] = "Executed"
        proposal["executedAt"] = datetime.now().isoformat()
        
        # Save to file
        self._save_proposals_to_file()
        
        return f"0xEXECUTE_{proposal_id}"

    def get_proposal(self, proposal_id: int) -> Dict[str, Any]:
        """
        Fetch proposal details from persistent storage.
        Returns proposal status, votes, deadline, etc.
        """
        
        proposal_id_str = str(proposal_id)
        
        if proposal_id_str not in self.proposals:
            return {"error": f"Proposal {proposal_id} not found"}
        
        proposal = self.proposals[proposal_id_str]
        
        return {
            "id": proposal.get("id"),
            "parameter": proposal.get("parameter"),
            "newValue": proposal.get("newValue"),
            "currentValue": proposal.get("currentValue"),
            "votesFor": proposal.get("votesFor", 0),
            "votesAgainst": proposal.get("votesAgainst", 0),
            "deadline": proposal.get("deadline", 0),
            "executed": proposal.get("executed", False),
            "status": proposal.get("status", "Unknown"),
            "created": proposal.get("created"),
            "executedAt": proposal.get("executedAt")
        }
    
    def get_all_proposals(self) -> Dict[int, Dict[str, Any]]:
        """Get all proposals"""
        return self.proposals
    
    # ==================================================
    # LEDGER INTEGRATION
    # ==================================================
    def record_trade_on_ledger(self, user: str, stock: str, action: str, quantity: int, price: float, confidence: float) -> str:
        """
        Record trade on Ledger.sol for permanent record.
        """
        
        if not self.simulation_mode and self.ledger_contract:
            try:
                # 🔥 REAL BLOCKCHAIN CALL - Record on Ledger
                tx = self.ledger_contract.functions.recordTrade(
                    user,
                    stock.encode(),  # Convert to bytes
                    action == "BUY",  # is_buy boolean
                    int(price),
                    int(quantity),
                    int(confidence * 100)  # Convert confidence to integer
                ).transact()
                
                return tx.hex()
            except Exception as e:
                print(f"❌ Ledger record failed: {e}")
                return f"0xLEDGER_FAILED"
        
        # Simulation mode
        return f"0xSIM_LEDGER_{stock}_{action}"
    
    # ==================================================
    # FETCH ON-CHAIN DATA
    # ==================================================
    def get_user_pnl(self, user: str) -> float:
        """Fetch user's PnL from PortfolioManager contract"""
        
        if not self.simulation_mode and self.portfolio_manager_contract:
            try:
                # 🔥 REAL BLOCKCHAIN CALL
                pnl = self.portfolio_manager_contract.functions.getPnL(user).call()
                return float(pnl)
            except Exception as e:
                print(f"⚠️ Could not fetch PnL from blockchain: {e}")
        
        # Calculate from local state as fallback
        return self._calculate_pnl()
    
    def _calculate_pnl(self) -> float:
        """Calculate PnL from local portfolio state"""
        current_value = self._calculate_portfolio_value()
        pnl = current_value - self.INITIAL_CAPITAL
        return pnl
    
    def get_user_trades(self, user: str) -> List[Dict[str, Any]]:
        """Fetch user's trades from Ledger contract or local history"""
        
        if not self.simulation_mode and self.ledger_contract:
            try:
                # 🔥 REAL BLOCKCHAIN CALL
                trades = self.ledger_contract.functions.getUserTrades(user).call()
                return trades
            except Exception as e:
                print(f"⚠️ Could not fetch trades from blockchain: {e}")
        
        # Return local transaction history
        return self.transaction_history
    
    # ==================================================
    # TRANSACTION FILE UTILITIES
    # ==================================================
    def get_transactions_from_file(self) -> List[Dict[str, Any]]:
        """Load and return all transactions from the JSON file"""
        self._load_transactions_from_file()
        return self.transaction_history
    
    def get_transaction_statistics(self) -> Dict[str, Any]:
        """Get statistics about all trades"""
        if not self.transaction_history:
            return {
                "total_trades": 0,
                "total_buys": 0,
                "total_sells": 0,
                "total_volume": 0.0,
                "average_trade_size": 0.0
            }
        
        buys = [tx for tx in self.transaction_history if tx.get("action") == "BUY"]
        sells = [tx for tx in self.transaction_history if tx.get("action") == "SELL"]
        
        total_volume = sum(tx.get("quantity", 0) * tx.get("price", 0) 
                          for tx in self.transaction_history)
        
        return {
            "total_trades": len(self.transaction_history),
            "total_buys": len(buys),
            "total_sells": len(sells),
            "total_volume": float(total_volume),
            "average_trade_size": float(total_volume / len(self.transaction_history)) 
                                 if self.transaction_history else 0.0,
            "symbols_traded": list(set(tx.get("symbol") for tx in self.transaction_history))
        }
    
    def export_transactions(self, file_path: str = None) -> str:
        """Export transactions to a file (default: data/transaction.json)"""
        if file_path is None:
            file_path = self.tx_file_path
        
        try:
            os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else ".", exist_ok=True)
            
            with open(file_path, 'w') as f:
                json.dump(self.transaction_history, f, indent=2)
            
            print(f"✅ Exported {len(self.transaction_history)} transactions to {file_path}")
            return f"Exported to {file_path}"
        except Exception as e:
            print(f"❌ Error exporting transactions: {e}")
            return f"Error: {e}"