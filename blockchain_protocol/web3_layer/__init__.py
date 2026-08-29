"""
Web3 Layer for Blockchain Protocol
Contains web3 provider and contract loaders
"""

from .web3_provider import get_web3_connection
from .contract_loader import ContractLoader
from .battery_contract_loader import BatteryContractLoader

__all__ = ['get_web3_connection', 'ContractLoader', 'BatteryContractLoader']
