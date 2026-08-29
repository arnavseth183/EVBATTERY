"""
Battery Contract Loader
Loads and manages EV Battery Passport smart contracts
"""

from typing import Optional, Dict, Any
from pathlib import Path
import json
from blockchain_protocol.web3_layer.web3_provider import get_web3_connection


class BatteryContractLoader:
    """Loader for EV Battery Passport smart contracts"""

    def __init__(self, web3=None):
        self.web3 = web3 if web3 else get_web3_connection()
        self.contracts = {}
        self.addresses_file = Path("blockchain_protocol/deployment/addresses.json")
        self._load_contract_addresses()

    def _load_contract_addresses(self):
        """Load deployed contract addresses"""
        try:
            if self.addresses_file.exists():
                with open(self.addresses_file, 'r') as f:
                    self.contract_addresses = json.load(f)
            else:
                self.contract_addresses = {}
        except Exception as e:
            print(f"⚠️ Could not load contract addresses: {e}")
            self.contract_addresses = {}

    def _load_abi(self, contract_name: str) -> Dict[str, Any]:
        """Load ABI from artifacts"""
        abi_file = Path(f"artifacts/contracts/{contract_name}.sol/{contract_name}.json")
        
        try:
            if abi_file.exists():
                with open(abi_file, 'r') as f:
                    contract_data = json.load(f)
                    return contract_data.get('abi', [])
            else:
                print(f"⚠️ ABI file not found for {contract_name}")
                return []
        except Exception as e:
            print(f"⚠️ Could not load ABI for {contract_name}: {e}")
            return []

    def get_contract(self, contract_name: str) -> Optional[Any]:
        """Get contract instance by name"""
        if contract_name in self.contracts:
            return self.contracts[contract_name]

        # Load ABI
        abi = self._load_abi(contract_name)
        if not abi:
            return None

        # Get address
        address = self.contract_addresses.get(contract_name)
        if not address:
            print(f"⚠️ No address found for {contract_name}")
            return None

        try:
            contract = self.web3.eth.contract(
                address=address,
                abi=abi
            )
            self.contracts[contract_name] = contract
            print(f"✅ Loaded contract: {contract_name} at {address}")
            return contract
        except Exception as e:
            print(f"❌ Could not load contract {contract_name}: {e}")
            return None

    def get_battery_user_registry(self):
        """Get BatteryUserRegistry contract"""
        return self.get_contract("BatteryUserRegistry")

    def get_battery_passport(self):
        """Get BatteryPassport contract"""
        return self.get_contract("BatteryPassport")

    def get_battery_governance(self):
        """Get BatteryGovernance contract"""
        return self.get_contract("BatteryGovernance")

    def deploy_contract(self, contract_name: str, *args) -> Optional[str]:
        """Deploy a contract (for development)"""
        try:
            abi = self._load_abi(contract_name)
            if not abi:
                return None

            # This would require compiled bytecode - simplified for now
            print(f"📝 Deployment of {contract_name} requires compiled bytecode")
            print(f"   Use deployment script instead")
            return None
        except Exception as e:
            print(f"❌ Could not deploy {contract_name}: {e}")
            return None

    def save_contract_address(self, contract_name: str, address: str):
        """Save deployed contract address"""
        self.contract_addresses[contract_name] = address
        
        try:
            self.addresses_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.addresses_file, 'w') as f:
                json.dump(self.contract_addresses, f, indent=2)
            print(f"✅ Saved address for {contract_name}: {address}")
        except Exception as e:
            print(f"❌ Could not save contract address: {e}")
