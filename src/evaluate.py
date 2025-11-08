"""Model evaluation utilities."""
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
import numpy as np
import json
import os

# Get project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def evaluate_model(model, X_test, y_test):
    """
    Evaluate model performance and return metrics.
    
    Args:
        model: Trained model pipeline
        X_test: Test features
        y_test: Test target values
    
    Returns:
        dict: Dictionary containing evaluation metrics
    """
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)
    # Calculate RMSE manually (squared=False parameter removed in newer sklearn versions)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    
    metrics = {
        "mae": float(mae),
        "r2": float(r2),
        "rmse": float(rmse)
    }
    
    print(f"📊 Model Performance Metrics:")
    print(f"   MAE: {mae:.2f}")
    print(f"   R²: {r2:.3f}")
    print(f"   RMSE: {rmse:.2f}")
    
    # Save metrics to file for monitoring
    metrics_path = "models/metrics.json"
    # Resolve path relative to project root if not absolute
    if not os.path.isabs(metrics_path):
        metrics_path = os.path.join(PROJECT_ROOT, metrics_path)
    os.makedirs(os.path.dirname(metrics_path), exist_ok=True)
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    
    return metrics

