"""
EV Battery Passport System - Unified Startup Script
Handles initialization, blockchain deployment, and dashboard launch
"""

import os
import subprocess
import time
import sys
from pathlib import Path
from typing import Optional
import json
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SystemStartup:
    """Manage complete system startup."""
    
    def __init__(self):
        """Initialize system startup manager."""
        self.root_dir = Path(__file__).parent.parent
        self.processes = []
        self.deployment_status = {
            "data_ready": False,
            "models_trained": False,
            "blockchain_running": False,
            "contracts_deployed": False,
            "dashboard_running": False
        }
    
    def print_banner(self):
        """Print startup banner."""
        banner = """
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║        🔋 EV BATTERY PASSPORT SYSTEM - UNIFIED STARTUP 🔋         ║
║                                                                    ║
║        Initializing Data Pipeline → ML → Blockchain → UI          ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met."""
        print("\n" + "="*70)
        print("🔍 CHECKING PREREQUISITES")
        print("="*70)
        
        checks = {
            "Python 3.8+": sys.version_info >= (3, 8),
            "requirements.txt": (self.root_dir / "requirements.txt").exists(),
            "config.py": (self.root_dir / "config.py").exists(),
            "Smart Contracts": (self.root_dir / "contracts").exists(),
            "Scripts": (self.root_dir / "scripts").exists(),
        }
        
        all_good = True
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"{status} {check}")
            if not passed:
                all_good = False
        
        return all_good
    
    def check_data(self) -> bool:
        """Check if data is generated and ready."""
        print("\n" + "="*70)
        print("📊 CHECKING DATA STATUS")
        print("="*70)
        
        data_files = [
            self.root_dir / "data/processed/battery_data_processed.csv",
            self.root_dir / "data/processed/battery_data_processed.json"
        ]
        
        for f in data_files:
            status = "✅" if f.exists() else "⏳"
            print(f"{status} {f.name}")
        
        if all(f.exists() for f in data_files):
            self.deployment_status["data_ready"] = True
            print("\n✅ Data is ready!")
            return True
        else:
            print("\n⏳ Data not found. Would you like to generate it? (y/n)")
            if input().strip().lower() == 'y':
                return self.generate_data()
            return False
    
    def generate_data(self) -> bool:
        """Generate synthetic battery data."""
        print("\n" + "="*70)
        print("🔄 GENERATING SYNTHETIC BATTERY DATA")
        print("="*70)
        
        try:
            import pandas as pd
            from scripts.battery_data_loader import BatteryDataLoader
            
            loader = BatteryDataLoader()
            df = loader.generate_sample_battery_data(num_batteries=100)
            
            # Validate
            valid_count = 0
            for _, record in df.iterrows():
                is_valid, _ = loader.validate_battery_record(record.to_dict())
                if is_valid:
                    valid_count += 1
            
            # Preprocess
            df = loader.preprocess_battery_data(df)
            
            # Save
            loader.save_processed_data(df)
            
            print(f"✅ Generated 100 battery records")
            print(f"✅ Validated {valid_count}/100 records")
            print(f"✅ Data saved to data/processed/")
            
            self.deployment_status["data_ready"] = True
            return True
        
        except Exception as e:
            logger.error(f"Error generating data: {e}")
            return False
    
    def check_models(self) -> bool:
        """Check if ML models are trained."""
        print("\n" + "="*70)
        print("🤖 CHECKING MODEL STATUS")
        print("="*70)
        
        model_files = list((self.root_dir / "models/trained").glob("demo_battery_health_model_*.pkl"))
        
        if model_files:
            print(f"✅ Health model found: {model_files[-1].name}")
            self.deployment_status["models_trained"] = True
            return True
        else:
            print("⏳ Models not found. Would you like to train them? (y/n)")
            if input().strip().lower() == 'y':
                return self.train_models()
            return False
    
    def train_models(self) -> bool:
        """Train ML models."""
        print("\n" + "="*70)
        print("🔄 TRAINING ML MODELS")
        print("="*70)
        
        try:
            from ai_oracle.training.battery_health_trainer import BatteryHealthTrainer
            
            trainer = BatteryHealthTrainer()
            trainer.train()
            
            print("✅ Models trained successfully!")
            self.deployment_status["models_trained"] = True
            return True
        
        except Exception as e:
            logger.error(f"Error training models: {e}")
            return False
    
    def setup_blockchain(self) -> bool:
        """Setup and start blockchain."""
        print("\n" + "="*70)
        print("⛓️  SETTING UP BLOCKCHAIN")
        print("="*70)
        
        # Check if docker is running
        try:
            result = subprocess.run(
                ["docker", "ps"],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                print("❌ Docker is not running. Please start Docker Desktop.")
                return False
        except Exception:
            print("⚠️  Docker not found. Install Docker Desktop to use blockchain.")
            return False
        
        print("✅ Docker is running")
        
        # Start docker-compose
        print("\n🔄 Starting blockchain node (docker-compose up)...")
        print("   This may take 30-60 seconds...")
        
        try:
            # Start in background
            self.compose_process = subprocess.Popen(
                ["docker-compose", "up"],
                cwd=str(self.root_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for blockchain to start
            time.sleep(10)
            
            # Check if process is still running
            if self.compose_process.poll() is None:
                print("✅ Blockchain node started")
                self.deployment_status["blockchain_running"] = True
                self.processes.append(self.compose_process)
                return True
            else:
                print("❌ Blockchain failed to start")
                return False
        
        except Exception as e:
            logger.error(f"Error starting blockchain: {e}")
            return False
    
    def deploy_contracts(self) -> bool:
        """Deploy smart contracts."""
        print("\n" + "="*70)
        print("📝 DEPLOYING SMART CONTRACTS")
        print("="*70)
        
        if not self.deployment_status["blockchain_running"]:
            print("⚠️  Blockchain not running. Skipping contract deployment.")
            return False
        
        print("🔄 Deploying contracts...")
        print("   This may take 20-30 seconds...")
        
        try:
            result = subprocess.run(
                ["python", "blockchain_protocol/deployment/deploy_protocol.py"],
                cwd=str(self.root_dir),
                capture_output=True,
                timeout=60,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Contracts deployed successfully")
                self.deployment_status["contracts_deployed"] = True
                return True
            else:
                print(f"❌ Contract deployment failed: {result.stderr}")
                return False
        
        except subprocess.TimeoutExpired:
            print("⚠️  Contract deployment timed out.")
            return False
        except Exception as e:
            logger.error(f"Error deploying contracts: {e}")
            return False
    
    def start_dashboard(self) -> bool:
        """Start Streamlit dashboard."""
        print("\n" + "="*70)
        print("🚀 STARTING DASHBOARD")
        print("="*70)
        
        try:
            print("🔄 Launching Streamlit dashboard...")
            print("   This may take 10-15 seconds...")
            
            self.dashboard_process = subprocess.Popen(
                ["streamlit", "run", "app.py", "--logger.level=error"],
                cwd=str(self.root_dir)
            )
            
            self.processes.append(self.dashboard_process)
            time.sleep(5)
            
            print("✅ Dashboard started")
            print("\n" + "="*70)
            print("🌐 DASHBOARD READY")
            print("="*70)
            print("📍 URL: http://localhost:8501")
            print("   Open this URL in your browser")
            print("="*70)
            
            self.deployment_status["dashboard_running"] = True
            return True
        
        except Exception as e:
            logger.error(f"Error starting dashboard: {e}")
            return False
    
    def display_status(self):
        """Display deployment status."""
        print("\n" + "="*70)
        print("📊 SYSTEM STATUS")
        print("="*70)
        
        status_map = {
            "data_ready": ("✅" if self.deployment_status["data_ready"] else "❌", "Data Pipeline"),
            "models_trained": ("✅" if self.deployment_status["models_trained"] else "❌", "ML Models"),
            "blockchain_running": ("✅" if self.deployment_status["blockchain_running"] else "❌", "Blockchain"),
            "contracts_deployed": ("✅" if self.deployment_status["contracts_deployed"] else "❌", "Smart Contracts"),
            "dashboard_running": ("✅" if self.deployment_status["dashboard_running"] else "❌", "Dashboard"),
        }
        
        for key, (symbol, name) in status_map.items():
            print(f"{symbol} {name}")
        
        print("="*70)
    
    def show_menu(self) -> str:
        """Display interactive menu."""
        print("\n" + "="*70)
        print("⚙️  SYSTEM MENU")
        print("="*70)
        print("1. Full Startup (All components)")
        print("2. Data Pipeline Only")
        print("3. Train Models Only")
        print("4. Start Blockchain + Contracts")
        print("5. Start Dashboard Only")
        print("6. Check Status")
        print("7. Exit")
        print("="*70)
        
        choice = input("\nSelect option (1-7): ").strip()
        return choice
    
    def run_full_startup(self):
        """Run full system startup."""
        print("\n🚀 Starting full system initialization...\n")
        
        steps = [
            ("Prerequisites", self.check_prerequisites),
            ("Data", self.check_data),
            ("Models", self.check_models),
            ("Blockchain", self.setup_blockchain),
            ("Contracts", self.deploy_contracts),
            ("Dashboard", self.start_dashboard),
        ]
        
        completed = []
        for step_name, step_func in steps:
            try:
                if step_func():
                    completed.append(step_name)
                else:
                    print(f"\n⚠️  {step_name} step incomplete. Continuing with next step...\n")
            except Exception as e:
                logger.error(f"Error in {step_name}: {e}")
                print(f"\n❌ Error in {step_name} step. Continuing...\n")
        
        self.display_status()
        
        if self.deployment_status["dashboard_running"]:
            print("\n" + "="*70)
            print("✅ SYSTEM READY!")
            print("="*70)
            print("\n📖 NEXT STEPS:")
            print("1. Open http://localhost:8501 in your browser")
            print("2. Create an account (save your private key)")
            print("3. Navigate to 'Add Battery' to enter battery data")
            print("4. View predictions and blockchain records")
            print("\n💡 FEATURES:")
            print("• Manual battery data entry with validation")
            print("• AI-powered SoH predictions")
            print("• Anomaly detection")
            print("• Blockchain storage")
            print("• Battery health analytics")
            print("="*70)
            
            print("\n🔄 Keeping system running. Press Ctrl+C to stop all services.")
            print("   Dashboard: http://localhost:8501")
            print("   Blockchain: http://localhost:8545 (if configured)")
            
            try:
                for proc in self.processes:
                    if proc:
                        proc.wait()
            except KeyboardInterrupt:
                print("\n\n⏹️  Shutting down services...")
                self.cleanup()
    
    def cleanup(self):
        """Clean up processes."""
        for proc in self.processes:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except:
                proc.kill()
    
    def run_interactive(self):
        """Run interactive mode."""
        self.print_banner()
        
        while True:
            choice = self.show_menu()
            
            if choice == "1":
                self.run_full_startup()
                break
            elif choice == "2":
                self.check_data()
            elif choice == "3":
                self.train_models()
            elif choice == "4":
                self.setup_blockchain()
                self.deploy_contracts()
            elif choice == "5":
                self.start_dashboard()
                try:
                    for proc in self.processes:
                        if proc:
                            proc.wait()
                except KeyboardInterrupt:
                    self.cleanup()
                break
            elif choice == "6":
                self.display_status()
            elif choice == "7":
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")


def main():
    """Main entry point."""
    startup = SystemStartup()
    
    # Auto-start if argument provided
    if len(sys.argv) > 1 and sys.argv[1] == "auto":
        startup.print_banner()
        startup.run_full_startup()
    else:
        # Interactive mode
        startup.run_interactive()


if __name__ == "__main__":
    main()
