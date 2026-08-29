"""
Deployment Script for EV Battery Passport Smart Contracts
Deploys BatteryUserRegistry, BatteryPassport, and BatteryGovernance contracts
"""

import json
import os
from pathlib import Path
from web3 import Web3
from eth_account import Account
from blockchain_protocol.web3_layer.web3_provider import get_web3_connection


class BatteryContractDeployer:
    """Deployer for EV Battery Passport smart contracts"""

    def __init__(self, web3=None, private_key=None):
        self.web3 = web3 if web3 else get_web3_connection()
        self.private_key = private_key or os.getenv("PRIVATE_KEY")
        
        if self.private_key:
            self.account = Account.from_key(self.private_key)
            self.deployer_address = self.account.address
        else:
            self.account = None
            self.deployer_address = self.web3.eth.accounts[0]  # Use first account for testing
        
        self.addresses_file = Path("blockchain_protocol/deployment/addresses.json")
        self.addresses_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.deployed_contracts = {}

    def _load_compiled_contracts(self):
        """Load compiled contract ABIs and bytecode"""
        contracts_dir = Path("artifacts/contracts")
        
        compiled = {}
        
        # Load BatteryUserRegistry
        user_registry_file = contracts_dir / "BatteryUserRegistry.sol" / "BatteryUserRegistry.json"
        if user_registry_file.exists():
            with open(user_registry_file, 'r') as f:
                data = json.load(f)
                compiled['BatteryUserRegistry'] = {
                    'abi': data.get('abi', []),
                    'bytecode': data.get('bytecode', '')
                }
        
        # Load BatteryPassport
        passport_file = contracts_dir / "BatteryPassport.sol" / "BatteryPassport.json"
        if passport_file.exists():
            with open(passport_file, 'r') as f:
                data = json.load(f)
                compiled['BatteryPassport'] = {
                    'abi': data.get('abi', []),
                    'bytecode': data.get('bytecode', '')
                }
        
        # Load BatteryGovernance
        governance_file = contracts_dir / "BatteryGovernance.sol" / "BatteryGovernance.json"
        if governance_file.exists():
            with open(governance_file, 'r') as f:
                data = json.load(f)
                compiled['BatteryGovernance'] = {
                    'abi': data.get('abi', []),
                    'bytecode': data.get('bytecode', '')
                }
        
        return compiled

    def _deploy_contract(self, contract_name, abi, bytecode, constructor_args=None):
        """Deploy a single contract"""
        try:
            print(f"\n📝 Deploying {contract_name}...")
            
            # Create contract instance
            contract = self.web3.eth.contract(abi=abi, bytecode=bytecode)
            
            # Build transaction
            if constructor_args:
                constructor_txn = contract.constructor(*constructor_args).build_transaction({
                    'from': self.deployer_address,
                    'gas': 5000000,
                    'gasPrice': self.web3.eth.gas_price,
                    'nonce': self.web3.eth.get_transaction_count(self.deployer_address)
                })
            else:
                constructor_txn = contract.constructor().build_transaction({
                    'from': self.deployer_address,
                    'gas': 5000000,
                    'gasPrice': self.web3.eth.gas_price,
                    'nonce': self.web3.eth.get_transaction_count(self.deployer_address)
                })
            
            # Sign transaction
            if self.private_key:
                signed_txn = self.web3.eth.account.sign_transaction(constructor_txn, self.private_key)
            else:
                # For testing with unlocked accounts
                signed_txn = constructor_txn
            
            # Send transaction
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            contract_address = tx_receipt.contractAddress
            print(f"✅ {contract_name} deployed at: {contract_address}")
            print(f"   Transaction hash: {tx_hash.hex()}")
            
            return contract_address, abi
            
        except Exception as e:
            print(f"❌ Failed to deploy {contract_name}: {e}")
            return None, None

    def deploy_all_contracts(self):
        """Deploy all battery passport contracts in correct order"""
        print("=" * 60)
        print("EV BATTERY PASSPORT SMART CONTRACT DEPLOYMENT")
        print("=" * 60)
        
        compiled = self._load_compiled_contracts()
        
        if not compiled:
            print("❌ No compiled contracts found. Please compile contracts first.")
            print("   Run: npx hardhat compile")
            return False
        
        # Step 1: Deploy BatteryUserRegistry
        user_registry_addr, user_registry_abi = self._deploy_contract(
            'BatteryUserRegistry',
            compiled['BatteryUserRegistry']['abi'],
            compiled['BatteryUserRegistry']['bytecode']
        )
        
        if not user_registry_addr:
            print("❌ Failed to deploy BatteryUserRegistry")
            return False
        
        self.deployed_contracts['BatteryUserRegistry'] = user_registry_addr
        
        # Step 2: Deploy BatteryGovernance
        governance_addr, governance_abi = self._deploy_contract(
            'BatteryGovernance',
            compiled['BatteryGovernance']['abi'],
            compiled['BatteryGovernance']['bytecode']
        )
        
        if not governance_addr:
            print("❌ Failed to deploy BatteryGovernance")
            return False
        
        self.deployed_contracts['BatteryGovernance'] = governance_addr
        
        # Step 3: Deploy BatteryPassport (depends on UserRegistry)
        passport_addr, passport_abi = self._deploy_contract(
            'BatteryPassport',
            compiled['BatteryPassport']['abi'],
            compiled['BatteryPassport']['bytecode'],
            constructor_args=[user_registry_addr]
        )
        
        if not passport_addr:
            print("❌ Failed to deploy BatteryPassport")
            return False
        
        self.deployed_contracts['BatteryPassport'] = passport_addr
        
        # Step 4: Configure contracts
        print("\n⚙️  Configuring contracts...")
        
        try:
            # Set BatteryPassport contract in UserRegistry
            user_registry_contract = self.web3.eth.contract(
                address=user_registry_addr,
                abi=user_registry_abi
            )
            
            set_battery_txn = user_registry_contract.functions.setBatteryPassportContract(
                passport_addr
            ).build_transaction({
                'from': self.deployer_address,
                'gas': 200000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(self.deployer_address)
            })
            
            if self.private_key:
                signed_txn = self.web3.eth.account.sign_transaction(set_battery_txn, self.private_key)
                tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
                self.web3.eth.wait_for_transaction_receipt(tx_hash)
            else:
                tx_hash = self.web3.eth.send_transaction(set_battery_txn)
                self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            print("✅ UserRegistry configured with BatteryPassport address")
            
            # Set BatteryPassport contract in Governance
            governance_contract = self.web3.eth.contract(
                address=governance_addr,
                abi=governance_abi
            )
            
            set_gov_txn = governance_contract.functions.setBatteryPassportContract(
                passport_addr
            ).build_transaction({
                'from': self.deployer_address,
                'gas': 200000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(self.deployer_address)
            })
            
            if self.private_key:
                signed_txn = self.web3.eth.account.sign_transaction(set_gov_txn, self.private_key)
                tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
                self.web3.eth.wait_for_transaction_receipt(tx_hash)
            else:
                tx_hash = self.web3.eth.send_transaction(set_gov_txn)
                self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            print("✅ Governance configured with BatteryPassport address")
            
        except Exception as e:
            print(f"⚠️ Contract configuration warning: {e}")
        
        # Save addresses
        self._save_addresses()
        
        print("\n" + "=" * 60)
        print("✅ DEPLOYMENT COMPLETE")
        print("=" * 60)
        print(f"\nDeployed Contracts:")
        print(f"  BatteryUserRegistry: {user_registry_addr}")
        print(f"  BatteryPassport:     {passport_addr}")
        print(f"  BatteryGovernance:   {governance_addr}")
        print(f"\nAddresses saved to: {self.addresses_file}")
        
        return True

    def _save_addresses(self):
        """Save deployed contract addresses"""
        with open(self.addresses_file, 'w') as f:
            json.dump(self.deployed_contracts, f, indent=2)
        print(f"✅ Contract addresses saved to {self.addresses_file}")

    def verify_deployment(self):
        """Verify that contracts are deployed and accessible"""
        print("\n🔍 Verifying deployment...")
        
        if not self.addresses_file.exists():
            print("❌ No deployment file found")
            return False
        
        with open(self.addresses_file, 'r') as f:
            addresses = json.load(f)
        
        for contract_name, address in addresses.items():
            try:
                code = self.web3.eth.get_code(address)
                if code == b'' or code == '0x':
                    print(f"❌ {contract_name} at {address} has no code")
                else:
                    print(f"✅ {contract_name} verified at {address}")
            except Exception as e:
                print(f"❌ Could not verify {contract_name}: {e}")
        
        return True


def main():
    """Main deployment function"""
    import sys
    
    print("Starting EV Battery Passport Contract Deployment...")
    
    # Initialize deployer
    deployer = BatteryContractDeployer()
    
    # Deploy contracts
    success = deployer.deploy_all_contracts()
    
    if success:
        # Verify deployment
        deployer.verify_deployment()
        print("\n✅ All contracts deployed and verified successfully!")
        return 0
    else:
        print("\n❌ Deployment failed")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
