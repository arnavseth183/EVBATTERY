"""
Quick script to train AI models
"""
from ai_oracle.training.battery_health_trainer import BatteryHealthTrainer
from scripts.battery_data_loader import BatteryDataLoader

print("Generating sample data...")
loader = BatteryDataLoader()
df_sample = loader.generate_sample_battery_data(num_batteries=200)
df_processed = loader.preprocess_battery_data(df_sample)

print("Training AI models...")
trainer = BatteryHealthTrainer()
X, y, feature_cols = trainer.prepare_features_for_health_prediction(df_processed)
health_results = trainer.train_health_model(X, y)
anomaly_results = trainer.train_anomaly_model(X, contamination=0.1)

print("Saving models...")
paths = trainer.save_models(prefix="demo_")

print("✅ AI models trained successfully!")
print(f"Test R²: {health_results['test_r2']:.4f}")
print(f"Detected anomalies: {anomaly_results['n_anomalies']}")
