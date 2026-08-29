"""
Battery Passport Controller
Refactored from trading protocol to focus on EV battery passport management
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import os
from pathlib import Path
from blockchain_protocol.web3_layer.battery_contract_loader import BatteryContractLoader
from blockchain_protocol.web3_layer.web3_provider import get_web3_connection


class BatteryPassportController:
    """Controller for EV Battery Passport operations with smart contract integration"""

    def __init__(self, config):
        self.config = config
        self.simulation_mode = getattr(config, "SIMULATION_MODE", True)
        
        # Battery storage paths
        self.battery_data_dir = Path(config.BATTERY_DATA_DIR)
        self.processed_data_dir = Path(config.PROCESSED_DATA_DIR)
        self.battery_passport_file = self.processed_data_dir / "battery_passports.json"
        self.qr_code_dir = self.processed_data_dir / "qr_codes"
        
        # Ensure directories exist
        self.battery_data_dir.mkdir(parents=True, exist_ok=True)
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)
        self.qr_code_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing battery passports
        self.battery_passports = {}
        self._load_battery_passports()
        
        # Smart contract integration
        self.web3 = get_web3_connection()
        self.contract_loader = BatteryContractLoader(self.web3)
        
        # Load contracts
        self.user_registry_contract = None
        self.battery_passport_contract = None
        self.governance_contract = None
        
        if not self.simulation_mode:
            self._load_contracts()
        
        print(f"✅ Battery Passport Controller initialized in {'SIMULATION' if self.simulation_mode else 'LIVE'} mode")

    def _load_contracts(self):
        """Load smart contracts for blockchain integration"""
        try:
            self.user_registry_contract = self.contract_loader.get_battery_user_registry()
            self.battery_passport_contract = self.contract_loader.get_battery_passport()
            self.governance_contract = self.contract_loader.get_battery_governance()
            print("✅ Smart contracts loaded successfully")
        except Exception as e:
            print(f"⚠️ Contract loading failed: {e}")
            self.user_registry_contract = None
            self.battery_passport_contract = None
            self.governance_contract = None

    def _load_battery_passports(self):
        """Load existing battery passports from file"""
        try:
            if self.battery_passport_file.exists():
                with open(self.battery_passport_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        self.battery_passports = json.loads(content)
                        print(f"✅ Loaded {len(self.battery_passports)} battery passports")
        except Exception as e:
            print(f"⚠️ Could not load battery passports: {e}")
            self.battery_passports = {}

    def _find_battery_in_files(self, passport_id: str) -> Optional[Dict[str, Any]]:
        """Find battery in external JSON files"""
        # Search in user entered batteries
        user_battery_file = self.processed_data_dir / "user_entered_batteries.json"
        if user_battery_file.exists():
            try:
                with open(user_battery_file, 'r') as f:
                    user_batteries = json.load(f)
                    for battery in user_batteries:
                        if battery.get('passport_id') == passport_id:
                            print(f"✅ Found battery in user_entered_batteries.json")
                            return battery
            except Exception as e:
                print(f"⚠️ Could not search user_entered_batteries.json: {e}")
        
        # Search in auto generated batteries
        auto_battery_file = self.processed_data_dir / "auto_generated_batteries.json"
        if auto_battery_file.exists():
            try:
                with open(auto_battery_file, 'r') as f:
                    auto_batteries = json.load(f)
                    for battery in auto_batteries:
                        if battery.get('passport_id') == passport_id:
                            print(f"✅ Found battery in auto_generated_batteries.json")
                            return battery
            except Exception as e:
                print(f"⚠️ Could not search auto_generated_batteries.json: {e}")
        
        # Search in processed data
        processed_file = self.processed_data_dir / "battery_data_processed.json"
        if processed_file.exists():
            try:
                with open(processed_file, 'r') as f:
                    processed_batteries = json.load(f)
                    if isinstance(processed_batteries, list):
                        for battery in processed_batteries:
                            if battery.get('passport_id') == passport_id:
                                print(f"✅ Found battery in battery_data_processed.json")
                                return battery
            except Exception as e:
                print(f"⚠️ Could not search battery_data_processed.json: {e}")
        
        print(f"❌ Battery {passport_id} not found in any file")
        return None

    def _save_battery_passports(self):
        """Save battery passports to file"""
        try:
            with open(self.battery_passport_file, 'w') as f:
                json.dump(self.battery_passports, f, indent=2)
            print(f"✅ Saved {len(self.battery_passports)} battery passports")
        except Exception as e:
            print(f"❌ Error saving battery passports: {e}")

    def create_battery_passport(self, battery_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new battery passport record
        Args:
            battery_data: Dictionary containing battery information
        Returns:
            Created passport record with passport_id
        """
        # Generate passport ID
        passport_id = f"EV-BATT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(self.battery_passports)}"
        
        # Add metadata
        passport_record = {
            "passport_id": passport_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "ACTIVE",
            "blockchain_registered": False,
            **battery_data
        }
        
        # Store passport
        self.battery_passports[passport_id] = passport_record
        self._save_battery_passports()
        
        print(f"✅ Created battery passport: {passport_id}")
        return passport_record

    def get_battery_passport(self, passport_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a battery passport by ID"""
        return self.battery_passports.get(passport_id)

    def update_battery_passport(self, passport_id: str, update_data: Dict[str, Any]) -> bool:
        """Update an existing battery passport"""
        if passport_id not in self.battery_passports:
            return False
        
        self.battery_passports[passport_id].update({
            **update_data,
            "updated_at": datetime.now().isoformat()
        })
        self._save_battery_passports()
        return True

    def get_all_batteries(self, user_wallet: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all battery passports, optionally filtered by user
        Args:
            user_wallet: Optional wallet address to filter by
        Returns:
            List of battery passport records
        """
        batteries = list(self.battery_passports.values())
        
        if user_wallet:
            batteries = [b for b in batteries if b.get("user_wallet") == user_wallet]
        
        return batteries

    def get_battery_health_summary(self, passport_id: str) -> Dict[str, Any]:
        """Get health summary for a specific battery"""
        passport = self.get_battery_passport(passport_id)
        if not passport:
            return {"error": "Passport not found"}
        
        soh = passport.get("soh", 0)
        cycles = passport.get("total_cycles", 0)
        temperature = passport.get("temperature_celsius", 0)
        
        # Calculate health status
        if soh >= 90:
            health_status = "EXCELLENT"
        elif soh >= 80:
            health_status = "GOOD"
        elif soh >= 70:
            health_status = "FAIR"
        elif soh >= 60:
            health_status = "DEGRADED"
        else:
            health_status = "POOR"
        
        # Temperature status
        if 15 <= temperature <= 35:
            temp_status = "OPTIMAL"
        elif temperature <= 50:
            temp_status = "WARNING"
        else:
            temp_status = "CRITICAL"
        
        return {
            "passport_id": passport_id,
            "soh": soh,
            "health_status": health_status,
            "temperature": temperature,
            "temperature_status": temp_status,
            "cycles": cycles,
            "degradation_rate": (100 - soh) / max(cycles, 1) if cycles > 0 else 0
        }

    def register_on_blockchain(self, passport_id: str) -> Dict[str, Any]:
        """
        Register battery passport on blockchain
        In simulation mode: Simulates registration
        In live mode: Interacts with BatteryPassport smart contract
        """
        # First try to find battery in internal storage
        if passport_id not in self.battery_passports:
            # Try to load from external JSON files
            battery = self._find_battery_in_files(passport_id)
            if not battery:
                return {"status": "FAILED", "error": "Passport not found"}
            # Add to internal storage
            self.battery_passports[passport_id] = battery
        else:
            battery = self.battery_passports[passport_id]
        
        if self.simulation_mode:
            # Simulate blockchain registration
            tx_hash = f"0xBATT_{len(self.battery_passports):064x}"
            
            self.battery_passports[passport_id]["blockchain_registered"] = True
            self.battery_passports[passport_id]["blockchain_tx"] = tx_hash
            self.battery_passports[passport_id]["blockchain_registered_at"] = datetime.now().isoformat()
            
            self._save_battery_passports()
            
            print(f"✅ Registered passport {passport_id} on blockchain (SIMULATION): {tx_hash}")
            return {
                "status": "SUCCESS",
                "tx_hash": tx_hash,
                "passport_id": passport_id,
                "mode": "SIMULATION"
            }
        else:
            # Live blockchain registration
            try:
                if not self.battery_passport_contract:
                    return {"status": "FAILED", "error": "Smart contract not loaded"}
                
                # Convert string addresses to proper format
                owner_address = battery.get("user_wallet", "0x0000000000000000000000000000000000000000")
                if not owner_address.startswith("0x"):
                    owner_address = "0x" + owner_address
                
                # Call smart contract
                tx_hash = self.battery_passport_contract.functions.registerBattery(
                    passport_id,
                    battery.get("manufacturer", "Unknown"),
                    battery.get("battery_type", "Unknown"),
                    int(battery.get("capacity_kwh", 0) * 100),  # Convert to integer
                    battery.get("production_date", "2024-01-01"),
                    int(battery.get("soh", 0)),
                    int(battery.get("soc", 0)),
                    int(battery.get("total_cycles", 0)),
                    int(battery.get("temperature_celsius", 0)),
                    battery.get("data_source", "manual")
                ).transact({'from': owner_address})
                
                self.battery_passports[passport_id]["blockchain_registered"] = True
                self.battery_passports[passport_id]["blockchain_tx"] = tx_hash.hex()
                self.battery_passports[passport_id]["blockchain_registered_at"] = datetime.now().isoformat()
                
                self._save_battery_passports()
                
                print(f"✅ Registered passport {passport_id} on blockchain (LIVE): {tx_hash.hex()}")
                return {
                    "status": "SUCCESS",
                    "tx_hash": tx_hash.hex(),
                    "passport_id": passport_id,
                    "mode": "LIVE"
                }
            except Exception as e:
                print(f"❌ Blockchain registration failed: {e}")
                return {
                    "status": "FAILED",
                    "error": str(e),
                    "passport_id": passport_id
                }

    def get_transaction_history(self) -> List[Dict[str, Any]]:
        """
        Get battery-related transaction history
        For blockchain explorer compatibility
        """
        transactions = []
        
        for passport_id, passport in self.battery_passports.items():
            if passport.get("blockchain_registered"):
                transactions.append({
                    "tx_hash": passport.get("blockchain_tx", ""),
                    "type": "BATTERY_REGISTRATION",
                    "passport_id": passport_id,
                    "timestamp": passport.get("blockchain_registered_at", passport.get("created_at")),
                    "user": passport.get("user_wallet", "system")
                })
        
        return transactions

    def get_portfolio_state(self):
        """
        Return state for compatibility with existing UI
        Refactored to return battery statistics instead of trading portfolio
        """
        batteries = self.get_all_batteries()
        
        if not batteries:
            return {
                "total_batteries": 0,
                "average_health": 0,
                "batteries": []
            }
        
        avg_soh = sum(b.get("soh", 0) for b in batteries) / len(batteries)
        
        return {
            "total_batteries": len(batteries),
            "average_health": avg_soh,
            "batteries": batteries
        }
