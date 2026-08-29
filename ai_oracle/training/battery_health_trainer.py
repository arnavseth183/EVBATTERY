"""
Battery Health Prediction Model
Trains ML models to predict State of Health (SoH) and detect anomalies in EV batteries.
"""

import numpy as np
import pandas as pd
import pickle
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple, List
import logging

from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.pipeline import Pipeline
import joblib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BatteryHealthTrainer:
    """Train and evaluate battery health prediction models."""
    
    def __init__(self, model_dir: str = "models/trained", scaler_dir: str = "models/scalers"):
        """
        Initialize battery health trainer.
        
        Args:
            model_dir: Directory to save trained models
            scaler_dir: Directory to save scalers
        """
        self.model_dir = Path(model_dir)
        self.scaler_dir = Path(scaler_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.scaler_dir.mkdir(parents=True, exist_ok=True)
        
        self.health_model = None
        self.health_scaler = None
        self.anomaly_model = None
        self.anomaly_scaler = None
        self.training_history = {}
        
        logger.info(f"BatteryHealthTrainer initialized")
    
    def load_training_data(self, filepath: str) -> pd.DataFrame:
        """Load training data from CSV or JSON."""
        logger.info(f"Loading training data from {filepath}")
        
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filepath.endswith('.json'):
            df = pd.read_json(filepath)
        else:
            raise ValueError("Unsupported file format. Use CSV or JSON.")
        
        logger.info(f"Loaded {len(df)} training samples")
        return df
    
    def prepare_features_for_health_prediction(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare features and targets for SoH prediction.
        
        Args:
            df: Battery data DataFrame
            
        Returns:
            Tuple of (X, y) for model training
        """
        logger.info("Preparing features for health prediction...")
        
        # Feature engineering
        df_features = df.copy()
        
        # Core features
        feature_cols = []
        
        # 1. Cycle-based features
        if 'total_cycles' in df_features.columns:
            feature_cols.append('total_cycles')
            # Cycles squared (non-linear relationship)
            df_features['cycles_squared'] = df_features['total_cycles'] ** 2
            feature_cols.append('cycles_squared')
        
        # 2. Temperature features
        if 'temperature_celsius' in df_features.columns:
            feature_cols.append('temperature_celsius')
            # Temperature squared for non-linearity
            df_features['temp_squared'] = df_features['temperature_celsius'] ** 2
            feature_cols.append('temp_squared')
        
        # 3. Capacity feature
        if 'capacity_kwh' in df_features.columns:
            feature_cols.append('capacity_kwh')
        
        # 4. Degradation rate
        if 'degradation_per_cycle' in df_features.columns:
            feature_cols.append('degradation_per_cycle')
        
        # 5. SoC features
        if 'soc' in df_features.columns:
            feature_cols.append('soc')
        
        # Remove rows with missing values
        df_features = df_features[feature_cols + ['soh']].dropna()
        
        if len(df_features) == 0:
            raise ValueError("No valid training data after feature preparation")
        
        X = df_features[feature_cols].values
        y = df_features['soh'].values
        
        logger.info(f"Prepared {X.shape[0]} samples with {X.shape[1]} features")
        logger.info(f"Feature columns: {feature_cols}")
        
        return X, y, feature_cols
    
    def train_health_model(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2) -> Dict:
        """
        Train RandomForest model for SoH prediction.
        
        Args:
            X: Feature matrix
            y: Target values (SoH)
            test_size: Test set fraction
            
        Returns:
            Dictionary with training results
        """
        logger.info("Training battery health prediction model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        logger.info(f"Train set: {X_train.shape[0]} samples, Test set: {X_test.shape[0]} samples")
        
        # Create pipeline with scaler
        self.health_scaler = StandardScaler()
        self.health_model = Pipeline([
            ('scaler', self.health_scaler),
            ('regressor', RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1,
                verbose=0
            ))
        ])
        
        # Train model
        self.health_model.fit(X_train, y_train)
        logger.info("✓ Model training complete")
        
        # Evaluate
        y_train_pred = self.health_model.predict(X_train)
        y_test_pred = self.health_model.predict(X_test)
        
        train_mse = mean_squared_error(y_train, y_train_pred)
        test_mse = mean_squared_error(y_test, y_test_pred)
        train_mae = mean_absolute_error(y_train, y_train_pred)
        test_mae = mean_absolute_error(y_test, y_test_pred)
        train_r2 = r2_score(y_train, y_train_pred)
        test_r2 = r2_score(y_test, y_test_pred)
        
        results = {
            'train_mse': train_mse,
            'test_mse': test_mse,
            'train_mae': train_mae,
            'test_mae': test_mae,
            'train_r2': train_r2,
            'test_r2': test_r2,
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'feature_count': X_train.shape[1]
        }
        
        logger.info(f"Training Results:")
        logger.info(f"  Train MSE: {train_mse:.4f}, Test MSE: {test_mse:.4f}")
        logger.info(f"  Train MAE: {train_mae:.4f}, Test MAE: {test_mae:.4f}")
        logger.info(f"  Train R²: {train_r2:.4f}, Test R²: {test_r2:.4f}")
        
        # Cross-validation
        kfold = KFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(self.health_model, X, y, cv=kfold, scoring='r2')
        
        results['cv_mean_r2'] = cv_scores.mean()
        results['cv_std_r2'] = cv_scores.std()
        logger.info(f"  Cross-validation R² (5-fold): {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        # Feature importance
        regressor = self.health_model.named_steps['regressor']
        feature_importance = regressor.feature_importances_
        results['feature_importance'] = feature_importance.tolist()
        
        self.training_history['health_model'] = results
        return results
    
    def train_anomaly_model(self, X: np.ndarray, contamination: float = 0.1) -> Dict:
        """
        Train Isolation Forest for anomaly detection.
        
        Args:
            X: Feature matrix
            contamination: Expected fraction of anomalies
            
        Returns:
            Dictionary with training results
        """
        logger.info("Training anomaly detection model...")
        
        # Create pipeline
        self.anomaly_scaler = RobustScaler()
        X_scaled = self.anomaly_scaler.fit_transform(X)
        
        self.anomaly_model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        
        self.anomaly_model.fit(X_scaled)
        logger.info("✓ Anomaly model training complete")
        
        # Get anomaly scores
        scores = self.anomaly_model.score_samples(X_scaled)
        predictions = self.anomaly_model.predict(X_scaled)
        
        n_anomalies = (predictions == -1).sum()
        anomaly_ratio = n_anomalies / len(predictions)
        
        results = {
            'n_anomalies': int(n_anomalies),
            'total_samples': len(predictions),
            'anomaly_ratio': float(anomaly_ratio),
            'contamination': contamination,
            'mean_score': float(scores.mean()),
            'std_score': float(scores.std()),
            'min_score': float(scores.min()),
            'max_score': float(scores.max())
        }
        
        logger.info(f"Anomaly Detection Results:")
        logger.info(f"  Detected anomalies: {n_anomalies}/{len(predictions)} ({anomaly_ratio:.2%})")
        logger.info(f"  Mean anomaly score: {scores.mean():.4f}")
        
        self.training_history['anomaly_model'] = results
        return results
    
    def save_models(self, prefix: str = "") -> Dict:
        """
        Save trained models and scalers.
        
        Args:
            prefix: Prefix for saved files
            
        Returns:
            Dictionary with saved file paths
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        paths = {}
        
        # Save health model
        if self.health_model is not None:
            model_path = self.model_dir / f"{prefix}battery_health_model_{timestamp}.pkl"
            joblib.dump(self.health_model, model_path)
            paths['health_model'] = str(model_path)
            logger.info(f"Saved health model: {model_path}")
        
        # Save health scaler
        if self.health_scaler is not None:
            scaler_path = self.scaler_dir / f"{prefix}health_scaler_{timestamp}.pkl"
            joblib.dump(self.health_scaler, scaler_path)
            paths['health_scaler'] = str(scaler_path)
            logger.info(f"Saved health scaler: {scaler_path}")
        
        # Save anomaly model
        if self.anomaly_model is not None:
            model_path = self.model_dir / f"{prefix}anomaly_model_{timestamp}.pkl"
            joblib.dump(self.anomaly_model, model_path)
            paths['anomaly_model'] = str(model_path)
            logger.info(f"Saved anomaly model: {model_path}")
        
        # Save anomaly scaler
        if self.anomaly_scaler is not None:
            scaler_path = self.scaler_dir / f"{prefix}anomaly_scaler_{timestamp}.pkl"
            joblib.dump(self.anomaly_scaler, scaler_path)
            paths['anomaly_scaler'] = str(scaler_path)
            logger.info(f"Saved anomaly scaler: {scaler_path}")
        
        # Save training history
        history_path = self.model_dir / f"{prefix}training_history_{timestamp}.pkl"
        joblib.dump(self.training_history, history_path)
        paths['training_history'] = str(history_path)
        logger.info(f"Saved training history: {history_path}")
        
        return paths
    
    def load_models(self, model_path: str, scaler_path: str, model_type: str = 'health'):
        """
        Load pre-trained models.
        
        Args:
            model_path: Path to model file
            scaler_path: Path to scaler file
            model_type: 'health' or 'anomaly'
        """
        if model_type == 'health':
            self.health_model = joblib.load(model_path)
            self.health_scaler = joblib.load(scaler_path)
            logger.info(f"Loaded health model from {model_path}")
        elif model_type == 'anomaly':
            self.anomaly_model = joblib.load(model_path)
            self.anomaly_scaler = joblib.load(scaler_path)
            logger.info(f"Loaded anomaly model from {model_path}")
    
    def predict_soh(self, X: np.ndarray) -> np.ndarray:
        """Predict SoH for new data."""
        if self.health_model is None:
            raise ValueError("Health model not trained or loaded")
        
        return self.health_model.predict(X)
    
    def predict_anomaly(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict anomalies for new data.
        
        Returns:
            Tuple of (predictions, scores) where -1 = anomaly, 1 = normal
        """
        if self.anomaly_model is None:
            raise ValueError("Anomaly model not trained or loaded")
        
        X_scaled = self.anomaly_scaler.transform(X)
        predictions = self.anomaly_model.predict(X_scaled)
        scores = self.anomaly_model.score_samples(X_scaled)
        
        return predictions, scores
    
    def get_model_summary(self) -> Dict:
        """Get summary of trained models."""
        return {
            'health_model_trained': self.health_model is not None,
            'anomaly_model_trained': self.anomaly_model is not None,
            'training_history': self.training_history
        }


# ==================== MAIN EXECUTION ====================

def main():
    """Demo: Train battery health and anomaly models."""
    
    print("=" * 80)
    print("Battery Health Prediction Model - Training Demo")
    print("=" * 80)
    
    # Generate sample data using processed data if available
    print("\n1. Loading battery data...")
    import os
    import sys
    
    # Add parent directory to path for imports
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    data_file = "data/processed/battery_data_processed.csv"
    
    if os.path.exists(data_file):
        print(f"   ✓ Found processed data: {data_file}")
        import pandas as pd
        df_processed = pd.read_csv(data_file)
    else:
        print(f"   ⚠ Data file not found. Generating new data...")
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from scripts.battery_data_loader import BatteryDataLoader
        
        loader = BatteryDataLoader()
        df_sample = loader.generate_sample_battery_data(num_batteries=200)
        df_processed = loader.preprocess_battery_data(df_sample)
    
    print(f"   ✓ Loaded {len(df_processed)} battery records")
    
    # Initialize trainer
    print("\n2. Initializing trainer...")
    trainer = BatteryHealthTrainer()
    print("   ✓ Trainer initialized")
    
    # Prepare features
    print("\n3. Preparing features...")
    X, y, feature_cols = trainer.prepare_features_for_health_prediction(df_processed)
    print(f"   ✓ Features prepared: {X.shape[0]} samples, {X.shape[1]} features")
    
    # Train health model
    print("\n4. Training health prediction model...")
    health_results = trainer.train_health_model(X, y)
    print(f"   ✓ Test R²: {health_results['test_r2']:.4f}")
    
    # Train anomaly model
    print("\n5. Training anomaly detection model...")
    anomaly_results = trainer.train_anomaly_model(X, contamination=0.1)
    print(f"   ✓ Detected {anomaly_results['n_anomalies']} anomalies")
    
    # Make predictions
    print("\n6. Testing predictions...")
    X_test = X[:5]  # Test on first 5 samples
    
    # SoH predictions
    soh_pred = trainer.predict_soh(X_test)
    print(f"   SoH Predictions (first 5):")
    for i, pred in enumerate(soh_pred):
        print(f"     Sample {i+1}: Predicted SoH = {pred:.2f}%")
    
    # Anomaly detection
    anomaly_pred, anomaly_scores = trainer.predict_anomaly(X_test)
    print(f"\n   Anomaly Detection (first 5):")
    for i, (pred, score) in enumerate(zip(anomaly_pred, anomaly_scores)):
        status = "ANOMALY" if pred == -1 else "NORMAL"
        print(f"     Sample {i+1}: {status} (score: {score:.4f})")
    
    # Save models
    print("\n7. Saving models...")
    paths = trainer.save_models(prefix="demo_")
    print(f"   ✓ Models saved:")
    for model_type, path in paths.items():
        print(f"     - {model_type}: {path}")
    
    # Summary
    print("\n8. Model Summary:")
    summary = trainer.get_model_summary()
    print(f"   Health model trained: {summary['health_model_trained']}")
    print(f"   Anomaly model trained: {summary['anomaly_model_trained']}")
    
    print("\n" + "=" * 80)
    print("✅ Battery health model training complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
