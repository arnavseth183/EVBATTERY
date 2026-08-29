import os
import json
from dotenv import load_dotenv

load_dotenv()


class AppConfig:

    # ------------------------------------------
    # GENERAL SETTINGS
    # ------------------------------------------

    APP_NAME = "EV Battery Passport System"
    DEBUG_MODE = True
    SIMULATION_MODE = False  # Set to False for proper blockchain connection

    # ------------------------------------------
    # BATTERY DATA PARAMETERS
    # ------------------------------------------

    # Battery types supported
    BATTERY_TYPES = [
        "Li-ion NCA",
        "Li-ion NCM",
        "Li-ion LFP",
        "Li-poly",
        "Solid-State"
    ]

    # Battery data collection interval
    DATA_COLLECTION_INTERVAL = "1h"  # Every hour
    DATA_RETENTION_DAYS = 365 * 10  # 10 years

    # Battery health thresholds
    BATTERY_HEALTH_THRESHOLDS = {
        "EXCELLENT": (90, 100),      # 90-100% SoH
        "GOOD": (80, 90),            # 80-90% SoH
        "FAIR": (70, 80),            # 70-80% SoH
        "DEGRADED": (60, 70),        # 60-70% SoH
        "POOR": (0, 60)              # Below 60% SoH
    }

    # Temperature safety thresholds (Celsius)
    TEMPERATURE_THRESHOLDS = {
        "OPTIMAL_MIN": 15,
        "OPTIMAL_MAX": 35,
        "WARNING_MAX": 50,
        "CRITICAL_MAX": 60
    }

    # ------------------------------------------
    # AI SETTINGS
    # ------------------------------------------

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Battery health prediction model
    BATTERY_HEALTH_MODEL_PATH = os.path.join(BASE_DIR, "models", "trained", "battery_health_model.pkl")
    BATTERY_ANOMALY_MODEL_PATH = os.path.join(BASE_DIR, "models", "trained", "battery_anomaly_model.pkl")
    
    # Feature scalers
    HEALTH_SCALER_PATH = os.path.join(BASE_DIR, "models", "scalers", "health_scaler.pkl")
    ANOMALY_SCALER_PATH = os.path.join(BASE_DIR, "models", "scalers", "anomaly_scaler.pkl")

    # Model confidence threshold
    HEALTH_PREDICTION_CONFIDENCE_THRESHOLD = 0.70
    ANOMALY_DETECTION_THRESHOLD = 0.75
    
    # Model retraining
    RETRAIN_INTERVAL_DAYS = 30

    # ------------------------------------------
    # BLOCKCHAIN SETTINGS
    # ------------------------------------------

    WEB3_PROVIDER_URI = os.getenv("WEB3_PROVIDER_URI")
    PRIVATE_KEY = os.getenv("PRIVATE_KEY")
    ACCOUNT_ADDRESS = os.getenv("ACCOUNT_ADDRESS")

    CONTRACT_ADDRESSES_FILE = os.path.join(
        BASE_DIR,
        "blockchain_protocol",
        "deployment",
        "addresses.json"
    )

    # Battery passport smart contracts
    BATTERY_USER_REGISTRY_CONTRACT = "BatteryUserRegistry"
    BATTERY_PASSPORT_CONTRACT = "BatteryPassport"
    BATTERY_GOVERNANCE_CONTRACT = "BatteryGovernance"

    # QR Code Server Configuration
    QR_SERVER_URL = os.getenv("QR_SERVER_URL", "http://localhost:8000")

    GAS_LIMIT = 3000000
    GAS_PRICE = None  # gwei

    # ------------------------------------------
    # SECURITY
    # ------------------------------------------

    ENCRYPTION_SECRET = os.getenv("ENCRYPTION_SECRET", "dev_secret_key")

    # ------------------------------------------
    # LOGGING
    # ------------------------------------------

    LOG_DIR = os.path.join(BASE_DIR, "logs")

    AI_LOG_FILE = os.path.join(LOG_DIR, "battery_health.log")
    BLOCKCHAIN_LOG_FILE = os.path.join(LOG_DIR, "blockchain.log")
    DATA_INGESTION_LOG_FILE = os.path.join(LOG_DIR, "data_ingestion.log")

    # ------------------------------------------
    # COMPLIANCE & REGULATORY
    # ------------------------------------------

    # Default to simulation mode for testing
    SIMULATION_MODE = True

    # Battery Passport standard compliance
    INCLUDE_BATTERY_PASSPORT_FIELDS = True
    REGULATORY_COMPLIANCE_MODE = "BATTERY_PASSPORT_2030"

    # ------------------------------------------
    # DATA STORAGE SETTINGS
    # ------------------------------------------

    DATA_STORAGE_FORMAT = "json"  # json / csv / blockchain
    DATA_DIR = os.path.join(BASE_DIR, "data")
    BATTERY_DATA_DIR = os.path.join(DATA_DIR, "battery_data")
    PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")

    # ------------------------------------------
    # IoT & QR CODE SETTINGS
    # ------------------------------------------

    IOT_ENABLED = True
    QR_CODE_ENABLED = True
    MQTT_BROKER_URL = os.getenv("MQTT_BROKER_URL", "localhost")
    MQTT_PORT = 1883

    # ------------------------------------------
    # EXECUTION SETTINGS
    # ------------------------------------------

    DEFAULT_EXECUTION_MODE = "manual"   # manual / auto
    AUTO_DATA_INGESTION_INTERVAL = 60  # seconds

    # ------------------------------------------
    # INIT
    # ------------------------------------------

    def __init__(self):
        self._ensure_directories()
        self._ensure_blockchain_files()
        self.validate()

    # ------------------------------------------
    # DIRECTORY SETUP
    # ------------------------------------------

    def _ensure_directories(self):
        os.makedirs(self.LOG_DIR, exist_ok=True)
        os.makedirs(self.BATTERY_DATA_DIR, exist_ok=True)
        os.makedirs(self.PROCESSED_DATA_DIR, exist_ok=True)
        os.makedirs(os.path.dirname(self.BATTERY_HEALTH_MODEL_PATH), exist_ok=True)
        os.makedirs(os.path.dirname(self.HEALTH_SCALER_PATH), exist_ok=True)

    # ------------------------------------------
    # BLOCKCHAIN FILE SETUP
    # ------------------------------------------

    def _ensure_blockchain_files(self):

        os.makedirs(os.path.dirname(self.CONTRACT_ADDRESSES_FILE), exist_ok=True)

        if not os.path.exists(self.CONTRACT_ADDRESSES_FILE):
            with open(self.CONTRACT_ADDRESSES_FILE, "w") as f:
                json.dump({}, f)

    # ------------------------------------------
    # VALIDATION
    # ------------------------------------------

    def validate(self):

        if not self.SIMULATION_MODE:

            if not self.WEB3_PROVIDER_URI:
                raise ValueError("WEB3_PROVIDER_URI not set in .env")

            if not self.PRIVATE_KEY:
                raise ValueError("PRIVATE_KEY not set in .env")

            if not self.ACCOUNT_ADDRESS:
                raise ValueError("ACCOUNT_ADDRESS not set in .env")

        if not os.path.exists(self.BATTERY_HEALTH_MODEL_PATH):
            print("Warning: Battery health model not found at", self.BATTERY_HEALTH_MODEL_PATH)

        if not os.path.exists(self.HEALTH_SCALER_PATH):
            print("Warning: Health scaler not found at", self.HEALTH_SCALER_PATH)

        if self.DEFAULT_EXECUTION_MODE not in ["manual", "auto"]:
            raise ValueError("DEFAULT_EXECUTION_MODE must be 'manual' or 'auto'")