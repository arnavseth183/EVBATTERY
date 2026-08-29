import os
import joblib
import numpy as np
import pandas as pd


class BatteryHealthPredictor:
    """Battery health prediction for EV Battery Passport system"""

    def __init__(self, config):

        self.config = config
        
        # Try to load the most recent model
        from pathlib import Path
        trained_dir = Path(config.BASE_DIR) / "models" / "trained"
        scaler_dir = Path(config.BASE_DIR) / "models" / "scalers"
        
        # Find the most recent model file
        model_files = sorted(trained_dir.glob("demo_battery_health_model_*.pkl"))
        scaler_files = sorted(scaler_dir.glob("demo_health_scaler_*.pkl"))
        
        model_path = model_files[-1] if model_files else None
        scaler_path = scaler_files[-1] if scaler_files else None

        self.model = None
        self.scaler = None

        # Load model safely
        if model_path and os.path.exists(model_path) and os.path.getsize(model_path) > 0:
            try:
                self.model = joblib.load(model_path)
                print(f"✓ Battery health model loaded: {model_path.name}")
            except Exception as e:
                print("Model load failed:", e)
        else:
            print("Battery health model file missing or empty. Running in mock mode.")

        # Load scaler safely
        if scaler_path and os.path.exists(scaler_path) and os.path.getsize(scaler_path) > 0:
            try:
                self.scaler = joblib.load(scaler_path)
                print(f"✓ Scaler loaded: {scaler_path.name}")
            except Exception as e:
                print("Scaler load failed:", e)
        else:
            print("Scaler file missing or empty.")

    # ------------------------------------------------
    # BATTERY HEALTH PREDICTION
    # ------------------------------------------------

    def predict_battery_health(self, battery_data):
        """
        Predict future battery State of Health (SoH) based on current parameters
        Args:
            battery_data: Dictionary with battery parameters (cycles, temperature, capacity, etc.)
        Returns:
            Dictionary with predicted future SoH and confidence
        """
        # Extract features
        cycles = battery_data.get("total_cycles", 0)
        temperature = battery_data.get("temperature_celsius", 25)
        capacity = battery_data.get("capacity_kwh", 75)
        soc = battery_data.get("soc", 50)
        
        # Calculate degradation rate
        current_soh = battery_data.get("soh", 85)
        degradation_rate = (100 - current_soh) / max(cycles, 1) if cycles > 0 else 0

        # Predict future SoH (after 100 additional cycles)
        future_cycles = cycles + 100
        
        if self.model is None or self.scaler is None:
            # Mock prediction - predict future degradation
            # Predict SoH after 100 more cycles
            additional_degradation = 100 * 0.015  # 1.5% degradation per 100 cycles
            future_soh = max(0, current_soh - additional_degradation + np.random.uniform(-2, 2))
            future_soh = max(0, min(100, future_soh))
            confidence = np.random.uniform(0.7, 0.95)
        else:
            # Real model prediction for future state
            try:
                features = [
                    future_cycles,
                    future_cycles ** 2,
                    temperature,
                    temperature ** 2,
                    capacity,
                    degradation_rate,
                    soc
                ]
                
                features_scaled = self.scaler.transform([features])
                future_soh = self.model.predict(features_scaled)[0]
                future_soh = max(0, min(100, future_soh))  # Clamp to 0-100
                confidence = 0.85  # Default confidence for real model
            except Exception as e:
                print(f"Prediction error: {e}")
                future_soh = current_soh - 5  # Fallback: assume 5% degradation
                confidence = 0.5

        # Determine future health status
        if future_soh >= 90:
            health_status = "EXCELLENT"
        elif future_soh >= 80:
            health_status = "GOOD"
        elif future_soh >= 70:
            health_status = "FAIR"
        elif future_soh >= 60:
            health_status = "DEGRADED"
        else:
            health_status = "POOR"

        return {
            "current_soh": round(current_soh, 2),
            "predicted_future_soh": round(future_soh, 2),
            "future_cycles": future_cycles,
            "health_status": health_status,
            "confidence": round(confidence, 2),
            "degradation_rate": round(degradation_rate, 4),
            "degradation_prediction": round(current_soh - future_soh, 2)
        }

    def predict_anomaly(self, battery_data):
        """
        Detect anomalies in battery behavior
        Args:
            battery_data: Dictionary with current battery readings
        Returns:
            Dictionary with anomaly detection results
        """
        # Simple anomaly detection based on thresholds
        soh = battery_data.get("soh", 85)
        temperature = battery_data.get("temperature_celsius", 25)
        cycles = battery_data.get("total_cycles", 0)
        
        anomalies = []
        
        # Temperature anomaly
        if temperature > 60:
            anomalies.append({
                "type": "CRITICAL_TEMPERATURE",
                "value": temperature,
                "threshold": 60,
                "severity": "HIGH"
            })
        elif temperature > 50:
            anomalies.append({
                "type": "HIGH_TEMPERATURE",
                "value": temperature,
                "threshold": 50,
                "severity": "MEDIUM"
            })
        
        # SoH anomaly
        if soh < 60 and cycles < 500:
            anomalies.append({
                "type": "PREMATURE_DEGRADATION",
                "value": soh,
                "expected_min": 80,
                "severity": "HIGH"
            })
        
        # Rapid degradation
        if cycles > 0:
            degradation_rate = (100 - soh) / cycles
            if degradation_rate > 0.1:  # More than 0.1% per cycle
                anomalies.append({
                    "type": "RAPID_DEGRADATION",
                    "value": degradation_rate,
                    "threshold": 0.1,
                    "severity": "MEDIUM"
                })
        
        return {
            "has_anomaly": len(anomalies) > 0,
            "anomalies": anomalies,
            "anomaly_count": len(anomalies)
        }


# Keep old class name for compatibility
Predictor = BatteryHealthPredictor