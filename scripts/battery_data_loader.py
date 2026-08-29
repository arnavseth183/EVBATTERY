"""
Battery Data Loader & Preprocessor
Handles ingestion, validation, and processing of EV battery data
from IoT sensors, QR codes, and manual input.
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BatteryDataLoader:
    """Load and preprocess battery data from various sources."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize battery data loader."""
        self.config = self._load_config(config_path)
        self.data_dir = Path(self.config.get("data_dir", "data/battery_data"))
        self.processed_dir = Path(self.config.get("processed_dir", "data/processed"))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Battery Data Loader initialized. Data dir: {self.data_dir}")
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from file or use defaults."""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        
        return {
            "battery_types": ["Li-ion NCA", "Li-ion NCM", "Li-ion LFP", "Li-poly", "Solid-State"],
            "data_dir": "data/battery_data",
            "processed_dir": "data/processed",
            "temperature_thresholds": {
                "optimal_min": 15,
                "optimal_max": 35,
                "warning_max": 50,
                "critical_max": 60
            },
            "health_thresholds": {
                "excellent": (90, 100),
                "good": (80, 90),
                "fair": (70, 80),
                "degraded": (60, 70),
                "poor": (0, 60)
            }
        }
    
    def generate_sample_battery_data(self, num_batteries: int = 100) -> pd.DataFrame:
        """
        Generate synthetic battery data for testing.
        
        Args:
            num_batteries: Number of batteries to generate
            
        Returns:
            DataFrame with battery records
        """
        logger.info(f"Generating {num_batteries} sample battery records...")
        
        battery_types = self.config["battery_types"]
        manufacturers = ["Tesla", "BYD", "LG", "Panasonic", "Samsung", "CATL"]
        
        records = []
        
        for i in range(num_batteries):
            # Generate passport ID
            passport_id = f"EV-BATT-{datetime.now().strftime('%Y%m%d')}-{i:05d}"
            
            # Base parameters
            manufacturer = np.random.choice(manufacturers)
            battery_type = np.random.choice(battery_types)
            capacity_kwh = np.random.uniform(50, 100)
            
            # Age-based degradation
            months_in_service = np.random.randint(0, 60)
            base_soh = 100 - (months_in_service * 0.5)  # ~0.5% degradation per month
            soh = np.clip(base_soh + np.random.normal(0, 2), 0, 100)
            
            # Current usage
            soc = np.random.uniform(10, 90)
            total_cycles = int(months_in_service * 10 + np.random.normal(0, 50))
            total_cycles = max(0, total_cycles)  # Ensure non-negative
            
            # Temperature (realistic range)
            temperature = np.random.normal(28, 5)
            temperature = np.clip(temperature, 15, 50)
            
            # Production date
            production_date = (datetime.now() - timedelta(days=months_in_service*30)).strftime('%Y-%m-%d')
            
            # Calculate health status
            health_status = self._get_health_status(soh)
            
            records.append({
                'passport_id': passport_id,
                'manufacturer': manufacturer,
                'battery_type': battery_type,
                'capacity_kwh': round(capacity_kwh, 2),
                'production_date': production_date,
                'soh': round(soh, 2),
                'soc': round(soc, 2),
                'total_cycles': total_cycles,
                'temperature_celsius': round(temperature, 2),
                'health_status': health_status,
                'timestamp': datetime.now().isoformat(),
                'data_source': 'simulated'
            })
        
        df = pd.DataFrame(records)
        logger.info(f"Generated {len(df)} sample battery records")
        return df
    
    def _get_health_status(self, soh: float) -> str:
        """Classify battery health status based on SoH."""
        thresholds = self.config["health_thresholds"]
        
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
    
    def validate_battery_record(self, record: Dict) -> Tuple[bool, List[str]]:
        """
        Validate a battery record against schema and constraints.
        
        Args:
            record: Battery data record as dictionary
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Required fields
        required_fields = [
            'passport_id', 'manufacturer', 'battery_type', 'capacity_kwh',
            'soh', 'soc', 'total_cycles', 'temperature_celsius'
        ]
        
        for field in required_fields:
            if field not in record:
                errors.append(f"Missing required field: {field}")
        
        # Validate ranges
        if 'soh' in record and not (0 <= record['soh'] <= 100):
            errors.append(f"SoH out of range (0-100): {record['soh']}")
        
        if 'soc' in record and not (0 <= record['soc'] <= 100):
            errors.append(f"SoC out of range (0-100): {record['soc']}")
        
        if 'temperature_celsius' in record:
            temp = record['temperature_celsius']
            thresholds = self.config["temperature_thresholds"]
            if temp > thresholds["critical_max"]:
                errors.append(f"Temperature CRITICAL: {temp}°C (max: {thresholds['critical_max']})")
        
        if 'capacity_kwh' in record and record['capacity_kwh'] <= 0:
            errors.append(f"Invalid capacity: {record['capacity_kwh']}")
        
        if 'total_cycles' in record and record['total_cycles'] < 0:
            errors.append(f"Invalid cycles: {record['total_cycles']}")
        
        return len(errors) == 0, errors
    
    def load_csv_data(self, filepath: str) -> pd.DataFrame:
        """
        Load battery data from CSV file.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            DataFrame with battery records
        """
        logger.info(f"Loading CSV data from {filepath}")
        
        try:
            df = pd.read_csv(filepath)
            logger.info(f"Loaded {len(df)} records from CSV")
            return df
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            raise
    
    def load_json_data(self, filepath: str) -> pd.DataFrame:
        """
        Load battery data from JSON file.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            DataFrame with battery records
        """
        logger.info(f"Loading JSON data from {filepath}")
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            df = pd.DataFrame(data)
            logger.info(f"Loaded {len(df)} records from JSON")
            return df
        except Exception as e:
            logger.error(f"Error loading JSON: {e}")
            raise
    
    def preprocess_battery_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess battery data (cleaning, validation, feature engineering).
        
        Args:
            df: Raw battery data DataFrame
            
        Returns:
            Preprocessed DataFrame
        """
        logger.info(f"Preprocessing {len(df)} battery records...")
        
        df_clean = df.copy()
        
        # Remove duplicates by passport_id
        initial_count = len(df_clean)
        df_clean = df_clean.drop_duplicates(subset=['passport_id'], keep='last')
        logger.info(f"Removed {initial_count - len(df_clean)} duplicate records")
        
        # Fill missing health_status
        if 'health_status' not in df_clean.columns:
            df_clean['health_status'] = df_clean['soh'].apply(self._get_health_status)
        
        # Add degradation rate feature
        if 'total_cycles' in df_clean.columns and 'soh' in df_clean.columns:
            df_clean['degradation_per_cycle'] = (100 - df_clean['soh']) / (df_clean['total_cycles'] + 1)
        
        # Add temperature category
        if 'temperature_celsius' in df_clean.columns:
            thresholds = self.config["temperature_thresholds"]
            df_clean['temperature_status'] = df_clean['temperature_celsius'].apply(
                lambda t: 'CRITICAL' if t > thresholds['critical_max']
                else 'WARNING' if t > thresholds['warning_max']
                else 'OPTIMAL' if thresholds['optimal_min'] <= t <= thresholds['optimal_max']
                else 'LOW'
            )
        
        # Convert timestamp to datetime
        if 'timestamp' in df_clean.columns:
            df_clean['timestamp'] = pd.to_datetime(df_clean['timestamp'])
        
        logger.info(f"Preprocessing complete. {len(df_clean)} records ready")
        return df_clean
    
    def save_processed_data(self, df: pd.DataFrame, output_name: str = "battery_data_processed") -> str:
        """
        Save processed data to CSV and JSON.
        
        Args:
            df: Processed DataFrame
            output_name: Base name for output files
            
        Returns:
            Path to saved CSV file
        """
        # Save as CSV
        csv_path = self.processed_dir / f"{output_name}.csv"
        df.to_csv(csv_path, index=False)
        logger.info(f"Saved processed data to CSV: {csv_path}")
        
        # Save as JSON
        json_path = self.processed_dir / f"{output_name}.json"
        df.to_json(json_path, orient='records', indent=2)
        logger.info(f"Saved processed data to JSON: {json_path}")
        
        return str(csv_path)
    
    def create_training_dataset(self, df: pd.DataFrame, target_col: str = 'soh') -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare data for ML model training.
        
        Args:
            df: Processed battery data
            target_col: Target column for prediction
            
        Returns:
            Tuple of (features, target)
        """
        logger.info(f"Creating training dataset with target: {target_col}")
        
        # Select feature columns
        feature_cols = [
            'capacity_kwh', 'total_cycles', 'temperature_celsius',
            'degradation_per_cycle'
        ]
        
        # Remove rows with missing features or target
        df_train = df[feature_cols + [target_col]].dropna()
        
        X = df_train[feature_cols].values
        y = df_train[target_col].values
        
        logger.info(f"Training dataset: {X.shape[0]} samples, {X.shape[1]} features")
        
        return X, y
    
    def get_battery_statistics(self, df: pd.DataFrame) -> Dict:
        """
        Generate statistical summary of battery data.
        
        Args:
            df: Battery data DataFrame
            
        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_batteries': len(df),
            'average_soh': df['soh'].mean() if 'soh' in df.columns else None,
            'min_soh': df['soh'].min() if 'soh' in df.columns else None,
            'max_soh': df['soh'].max() if 'soh' in df.columns else None,
            'average_cycles': df['total_cycles'].mean() if 'total_cycles' in df.columns else None,
            'average_temperature': df['temperature_celsius'].mean() if 'temperature_celsius' in df.columns else None,
            'health_status_breakdown': df['health_status'].value_counts().to_dict() if 'health_status' in df.columns else {},
            'manufacturer_breakdown': df['manufacturer'].value_counts().to_dict() if 'manufacturer' in df.columns else {},
            'battery_type_breakdown': df['battery_type'].value_counts().to_dict() if 'battery_type' in df.columns else {}
        }
        
        return stats
    
    def export_report(self, df: pd.DataFrame, output_path: str = None) -> str:
        """
        Export battery data summary report.
        
        Args:
            df: Battery data DataFrame
            output_path: Output file path
            
        Returns:
            Path to saved report
        """
        stats = self.get_battery_statistics(df)
        
        if output_path is None:
            output_path = self.processed_dir / f"battery_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_path, 'w') as f:
            json.dump(stats, f, indent=2, default=str)
        
        logger.info(f"Report saved to: {output_path}")
        return str(output_path)


# ==================== MAIN EXECUTION ====================

def main():
    """Demo: Generate, load, process, and save battery data."""
    
    print("=" * 80)
    print("EV Battery Data Loader - Demo")
    print("=" * 80)
    
    # Initialize loader
    loader = BatteryDataLoader()
    
    # Generate sample data
    print("\n1. Generating sample battery data...")
    df_sample = loader.generate_sample_battery_data(num_batteries=100)
    print(f"   ✓ Generated {len(df_sample)} battery records")
    print(f"\n   Sample record:\n{df_sample.iloc[0].to_string()}\n")
    
    # Validate samples
    print("2. Validating battery records...")
    valid_count = 0
    for idx, record in df_sample.iterrows():
        is_valid, errors = loader.validate_battery_record(record.to_dict())
        if is_valid:
            valid_count += 1
        else:
            print(f"   ⚠ Record {idx} has errors: {errors}")
    print(f"   ✓ {valid_count}/{len(df_sample)} records are valid")
    
    # Preprocess data
    print("\n3. Preprocessing battery data...")
    df_processed = loader.preprocess_battery_data(df_sample)
    print(f"   ✓ Preprocessing complete")
    print(f"   New columns: {[col for col in df_processed.columns if col not in df_sample.columns]}\n")
    
    # Save processed data
    print("4. Saving processed data...")
    csv_path = loader.save_processed_data(df_processed)
    print(f"   ✓ Data saved to:\n     - {csv_path}\n     - {csv_path.replace('.csv', '.json')}")
    
    # Generate statistics
    print("\n5. Battery Statistics:")
    stats = loader.get_battery_statistics(df_processed)
    print(f"   Total Batteries: {stats['total_batteries']}")
    print(f"   Average SoH: {stats['average_soh']:.2f}%")
    print(f"   Average Cycles: {stats['average_cycles']:.0f}")
    print(f"   Average Temperature: {stats['average_temperature']:.1f}°C")
    print(f"\n   Health Status Breakdown:")
    for status, count in stats['health_status_breakdown'].items():
        print(f"     - {status}: {count}")
    
    # Export report
    print("\n6. Exporting report...")
    report_path = loader.export_report(df_processed)
    print(f"   ✓ Report exported to: {report_path}")
    
    print("\n" + "=" * 80)
    print("✅ Battery data loading and preprocessing complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
