"""
Interactive Battery Data Input Module
Allows users to manually enter battery data through command line interface
"""

import pandas as pd
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.battery_data_loader import BatteryDataLoader


class InteractiveBatteryInput:
    """Handle interactive battery data entry from users."""
    
    def __init__(self):
        """Initialize the interactive input handler."""
        self.data_loader = BatteryDataLoader()
        self.battery_types = self.data_loader.config["battery_types"]
        self.manufacturers = ["Tesla", "BYD", "LG", "Panasonic", "Samsung", "CATL", "Other"]
        self.health_thresholds = self.data_loader.config["health_thresholds"]
        self.data_file = Path("data/processed/user_entered_batteries.json")
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
    
    def get_battery_types_menu(self) -> str:
        """Display battery types menu and get user choice."""
        print("\n" + "="*60)
        print("🔋 BATTERY TYPES")
        print("="*60)
        
        for i, btype in enumerate(self.battery_types, 1):
            print(f"{i}. {btype}")
        print(f"{len(self.battery_types) + 1}. Enter custom type")
        
        while True:
            try:
                choice = int(input("\nSelect battery type (number): "))
                if 1 <= choice <= len(self.battery_types):
                    return self.battery_types[choice - 1]
                elif choice == len(self.battery_types) + 1:
                    custom = input("Enter custom battery type: ").strip()
                    if custom:
                        return custom
                    print("❌ Invalid input. Please try again.")
                else:
                    print("❌ Invalid choice. Please try again.")
            except ValueError:
                print("❌ Please enter a valid number.")
    
    def get_manufacturer_menu(self) -> str:
        """Display manufacturers menu and get user choice."""
        print("\n" + "="*60)
        print("🏭 MANUFACTURER")
        print("="*60)
        
        for i, mfr in enumerate(self.manufacturers, 1):
            print(f"{i}. {mfr}")
        
        while True:
            try:
                choice = int(input("\nSelect manufacturer (number): "))
                if 1 <= choice <= len(self.manufacturers):
                    if self.manufacturers[choice - 1] == "Other":
                        custom = input("Enter manufacturer name: ").strip()
                        if custom:
                            return custom
                        print("❌ Invalid input. Please try again.")
                    else:
                        return self.manufacturers[choice - 1]
                else:
                    print("❌ Invalid choice. Please try again.")
            except ValueError:
                print("❌ Please enter a valid number.")
    
    def get_float_input(self, prompt: str, min_val: float = None, max_val: float = None) -> float:
        """Get validated float input from user."""
        while True:
            try:
                value = float(input(prompt))
                if min_val is not None and value < min_val:
                    print(f"❌ Value must be >= {min_val}")
                    continue
                if max_val is not None and value > max_val:
                    print(f"❌ Value must be <= {max_val}")
                    continue
                return value
            except ValueError:
                print("❌ Please enter a valid number.")
    
    def get_int_input(self, prompt: str, min_val: int = None, max_val: int = None) -> int:
        """Get validated integer input from user."""
        while True:
            try:
                value = int(input(prompt))
                if min_val is not None and value < min_val:
                    print(f"❌ Value must be >= {min_val}")
                    continue
                if max_val is not None and value > max_val:
                    print(f"❌ Value must be <= {max_val}")
                    continue
                return value
            except ValueError:
                print("❌ Please enter a valid integer.")
    
    def collect_battery_data(self) -> Dict:
        """Interactively collect battery data from user."""
        print("\n" + "="*60)
        print("📝 ENTER BATTERY DATA")
        print("="*60)
        
        # Passport ID (auto-generated)
        passport_id = f"EV-BATT-{datetime.now().strftime('%Y%m%d%H%M%S')}-USER"
        print(f"\nPassport ID (auto-generated): {passport_id}")
        
        # Battery Type
        battery_type = self.get_battery_types_menu()
        print(f"✓ Battery Type: {battery_type}")
        
        # Manufacturer
        manufacturer = self.get_manufacturer_menu()
        print(f"✓ Manufacturer: {manufacturer}")
        
        # Capacity (kWh)
        print("\n" + "="*60)
        print("📊 SPECIFICATIONS")
        print("="*60)
        capacity_kwh = self.get_float_input(
            "Battery Capacity (kWh) [50-150]: ",
            min_val=50, max_val=150
        )
        print(f"✓ Capacity: {capacity_kwh} kWh")
        
        # State of Health (SoH) - %
        soh = self.get_float_input(
            "State of Health (SoH) [0-100%]: ",
            min_val=0, max_val=100
        )
        print(f"✓ SoH: {soh}%")
        
        # State of Charge (SoC) - %
        soc = self.get_float_input(
            "State of Charge (SoC) [0-100%]: ",
            min_val=0, max_val=100
        )
        print(f"✓ SoC: {soc}%")
        
        # Total Cycles
        total_cycles = self.get_int_input(
            "Total Charge Cycles [0-10000]: ",
            min_val=0, max_val=10000
        )
        print(f"✓ Total Cycles: {total_cycles}")
        
        # Temperature (°C)
        print("\n" + "="*60)
        print("🌡️  TEMPERATURE & CONDITIONS")
        print("="*60)
        temperature = self.get_float_input(
            "Current Temperature (°C) [10-60]: ",
            min_val=10, max_val=60
        )
        print(f"✓ Temperature: {temperature}°C")
        
        # Calculate degradation per cycle
        degradation_per_cycle = (100 - soh) / max(total_cycles, 1)
        
        # Determine health status
        health_status = self._get_health_status(soh)
        
        # Determine temperature status
        temp_status = self._get_temperature_status(temperature)
        
        # Production Date
        prod_date = input("\nProduction Date (YYYY-MM-DD) [or press Enter for today]: ").strip()
        if not prod_date:
            prod_date = datetime.now().strftime('%Y-%m-%d')
        print(f"✓ Production Date: {prod_date}")
        
        # Compile record
        record = {
            'passport_id': passport_id,
            'manufacturer': manufacturer,
            'battery_type': battery_type,
            'capacity_kwh': round(capacity_kwh, 2),
            'production_date': prod_date,
            'soh': round(soh, 2),
            'soc': round(soc, 2),
            'total_cycles': total_cycles,
            'temperature_celsius': round(temperature, 2),
            'health_status': health_status,
            'temperature_status': temp_status,
            'degradation_per_cycle': round(degradation_per_cycle, 4),
            'timestamp': datetime.now().isoformat(),
            'data_source': 'user_input'
        }
        
        return record
    
    def _get_health_status(self, soh: float) -> str:
        """Classify battery health status based on SoH."""
        thresholds = self.health_thresholds
        
        if thresholds["excellent"][0] <= soh <= thresholds["excellent"][1]:
            return "EXCELLENT"
        elif thresholds["good"][0] <= soh <= thresholds["good"][1]:
            return "GOOD"
        elif thresholds["fair"][0] <= soh <= thresholds["fair"][1]:
            return "FAIR"
        elif thresholds["degraded"][0] <= soh <= thresholds["degraded"][1]:
            return "DEGRADED"
        else:
            return "POOR"
    
    def _get_temperature_status(self, temp: float) -> str:
        """Classify temperature status."""
        if 15 <= temp <= 35:
            return "OPTIMAL"
        elif 35 < temp <= 50:
            return "WARNING"
        else:
            return "CRITICAL"
    
    def save_battery_data(self, record: Dict) -> bool:
        """Save battery record to file."""
        try:
            # Load existing data
            existing_data = []
            if self.data_file.exists():
                with open(self.data_file, 'r') as f:
                    existing_data = json.load(f)
            
            # Add new record
            existing_data.append(record)
            
            # Save back
            with open(self.data_file, 'w') as f:
                json.dump(existing_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"❌ Error saving data: {e}")
            return False
    
    def validate_record(self, record: Dict) -> tuple:
        """Validate the battery record."""
        is_valid, errors = self.data_loader.validate_battery_record(record)
        return is_valid, errors
    
    def display_summary(self, record: Dict):
        """Display battery record summary."""
        print("\n" + "="*60)
        print("✅ BATTERY RECORD SUMMARY")
        print("="*60)
        print(f"Passport ID:       {record['passport_id']}")
        print(f"Manufacturer:      {record['manufacturer']}")
        print(f"Battery Type:      {record['battery_type']}")
        print(f"Capacity:          {record['capacity_kwh']} kWh")
        print(f"State of Health:   {record['soh']}%")
        print(f"State of Charge:   {record['soc']}%")
        print(f"Total Cycles:      {record['total_cycles']}")
        print(f"Temperature:       {record['temperature_celsius']}°C")
        print(f"Health Status:     {record['health_status']}")
        print(f"Temperature Status: {record['temperature_status']}")
        print(f"Degradation/Cycle: {record['degradation_per_cycle']}%")
        print(f"Entered at:        {record['timestamp']}")
        print("="*60)
    
    def run_interactive_session(self):
        """Run an interactive data entry session."""
        print("\n" + "🔋 "*20)
        print("EV BATTERY PASSPORT - INTERACTIVE DATA ENTRY".center(60))
        print("🔋 "*20)
        
        batteries_added = 0
        
        while True:
            try:
                # Collect data
                record = self.collect_battery_data()
                
                # Validate
                is_valid, errors = self.validate_record(record)
                
                if not is_valid:
                    print("\n❌ VALIDATION ERRORS:")
                    for error in errors:
                        print(f"  - {error}")
                    
                    retry = input("\nRetry? (y/n): ").strip().lower()
                    if retry == 'y':
                        continue
                    else:
                        break
                
                # Display summary
                self.display_summary(record)
                
                # Confirm save
                save = input("\nSave this battery record? (y/n): ").strip().lower()
                if save == 'y':
                    if self.save_battery_data(record):
                        print("✅ Battery record saved successfully!")
                        batteries_added += 1
                    else:
                        print("❌ Failed to save battery record.")
                else:
                    print("⏭️  Record discarded.")
                
                # Ask to add another
                another = input("\nAdd another battery? (y/n): ").strip().lower()
                if another != 'y':
                    break
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Session interrupted by user.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                break
        
        # Final summary
        print("\n" + "="*60)
        print(f"SESSION COMPLETE - {batteries_added} battery(ies) added")
        print(f"Data saved to: {self.data_file}")
        print("="*60)


def main():
    """Main entry point."""
    input_handler = InteractiveBatteryInput()
    input_handler.run_interactive_session()


if __name__ == "__main__":
    main()
