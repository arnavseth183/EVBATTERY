"""
logging_config.py
=================
Centralized logging configuration for DAPPTRADE
Separates transaction logs from account logs
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# ====================================================
# TRANSACTION LOGGER
# ====================================================
def get_transaction_logger():
    """
    Separate logger for all trade transactions
    Logs: BUY/SELL orders, executions, confirmations
    File: logs/transactions.log
    """
    logger = logging.getLogger("transactions")
    
    if logger.hasHandlers():
        return logger  # Return if already configured
    
    logger.setLevel(logging.INFO)
    
    # File handler with rotation
    transaction_file = os.path.join(LOG_DIR, "transactions.log")
    file_handler = RotatingFileHandler(
        transaction_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    
    # Log format for transactions
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler for console output with UTF-8 encoding
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    if hasattr(console_handler, 'setEncoding'):
        console_handler.setEncoding('utf-8')
    logger.addHandler(console_handler)
    
    return logger


# ====================================================
# ACCOUNT LOGGER
# ====================================================
def get_account_logger():
    """
    Separate logger for all account operations
    Logs: User creation, login, password reset, wallet operations
    File: logs/accounts.log
    """
    logger = logging.getLogger("accounts")
    
    if logger.hasHandlers():
        return logger  # Return if already configured
    
    logger.setLevel(logging.INFO)
    
    # File handler with rotation
    account_file = os.path.join(LOG_DIR, "accounts.log")
    file_handler = RotatingFileHandler(
        account_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    
    # Log format for accounts
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler for console output with UTF-8 encoding
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    if hasattr(console_handler, 'setEncoding'):
        console_handler.setEncoding('utf-8')
    logger.addHandler(console_handler)
    
    return logger


# ====================================================
# BLOCKCHAIN LOGGER
# ====================================================
def get_blockchain_logger():
    """
    Logger for blockchain operations
    Logs: Contract calls, gas estimates, network info
    File: logs/blockchain.log
    """
    logger = logging.getLogger("blockchain")
    
    if logger.hasHandlers():
        return logger
    
    logger.setLevel(logging.INFO)
    
    blockchain_file = os.path.join(LOG_DIR, "blockchain.log")
    file_handler = RotatingFileHandler(
        blockchain_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler for console output with UTF-8 encoding
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    if hasattr(console_handler, 'setEncoding'):
        console_handler.setEncoding('utf-8')
    logger.addHandler(console_handler)
    
    return logger


# ====================================================
# APP LOGGER (General)
# ====================================================
def get_app_logger():
    """
    General application logger
    File: logs/app.log
    """
    logger = logging.getLogger("app")
    
    if logger.hasHandlers():
        return logger
    
    logger.setLevel(logging.INFO)
    
    app_file = os.path.join(LOG_DIR, "app.log")
    file_handler = RotatingFileHandler(
        app_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler for console output with UTF-8 encoding
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    if hasattr(console_handler, 'setEncoding'):
        console_handler.setEncoding('utf-8')
    logger.addHandler(console_handler)
    
    return logger


# ====================================================
# GOVERNANCE LOGGER
# ====================================================
def get_governance_logger():
    """
    Logger for governance operations
    Logs: Proposal creation, voting, parameter changes
    File: logs/governance.log
    """
    logger = logging.getLogger("governance")
    
    if logger.hasHandlers():
        return logger
    
    logger.setLevel(logging.INFO)
    
    governance_file = os.path.join(LOG_DIR, "governance.log")
    file_handler = RotatingFileHandler(
        governance_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler for console output with UTF-8 encoding
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    if hasattr(console_handler, 'setEncoding'):
        console_handler.setEncoding('utf-8')
    logger.addHandler(console_handler)
    
    return logger
