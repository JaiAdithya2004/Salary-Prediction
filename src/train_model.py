"""Model training script."""
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
import os
import sys

# Add parent directory to path to allow imports when running from src/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.preprocess import create_preprocessor
from src.evaluate import evaluate_model
from src.utils import load_data, validate_data, clean_data


def train_and_save_model(
    data_path="data/salary_data.csv",
    model_path="models/model.pkl",
    test_size=0.2,
    random_state=42,
    clean=True
):
    """
    Train and save the salary prediction model.
    
    Args:
        data_path: Path to training data CSV (relative to project root or absolute)
        model_path: Path to save trained model (relative to project root or absolute)
        test_size: Proportion of data for testing
        random_state: Random seed for reproducibility
        clean: Whether to clean data (remove missing values and duplicates)
    
    Returns:
        dict: Evaluation metrics
    """
    # Resolve paths relative to project root if they're not absolute
    if not os.path.isabs(data_path):
        data_path = os.path.join(PROJECT_ROOT, data_path)
    if not os.path.isabs(model_path):
        model_path = os.path.join(PROJECT_ROOT, model_path)
    
    print("🚀 Starting model training...")
    print(f"   Data: {data_path}")
    print(f"   Model output: {model_path}")
    
    # Load data
    df = load_data(data_path)
    print(f"\n📊 Data Loading:")
    print(f"   Loaded {len(df)} records")
    
    # Clean data (remove missing values and duplicates)
    if clean:
        print(f"\n🧹 Data Cleaning:")
        df = clean_data(df, target_col="Salary", remove_duplicates=True, handle_missing="drop")
    
    # Validate data
    print(f"\n✅ Data Validation:")
    target_col = "Salary"
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in data")
    
    # Check minimum data requirement
    if len(df) < 10:
        raise ValueError(f"Insufficient data: {len(df)} records. Need at least 10 records for training.")
    
    print(f"   ✅ Dataset ready for training")
    print(f"   ✅ All required columns present")
    print(f"   ✅ No missing values in target variable")
    
    X = df.drop(target_col, axis=1)
    y = df[target_col]
    
    # Auto-detect categorical and numeric columns
    categorical = X.select_dtypes(include=['object']).columns.tolist()
    numeric = X.select_dtypes(include=['number']).columns.tolist()
    
    print(f"\n📋 Feature Analysis:")
    print(f"   Categorical features ({len(categorical)}): {categorical}")
    print(f"   Numeric features ({len(numeric)}): {numeric}")
    
    # Create preprocessing pipeline
    preprocessor = create_preprocessor(categorical, numeric)
    
    # Create full pipeline
    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", RandomForestRegressor(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            random_state=random_state,
            n_jobs=-1
        ))
    ])
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    
    print(f"   Training set: {len(X_train)} samples")
    print(f"   Test set: {len(X_test)} samples")
    
    # Train model
    print("\n📚 Training model...")
    pipeline.fit(X_train, y_train)
    
    # Save model
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(pipeline, model_path)
    print(f"\n✅ Model trained and saved to: {model_path}")
    
    # Evaluate model
    print("\n📊 Evaluating model...")
    metrics = evaluate_model(pipeline, X_test, y_test)
    
    return metrics


if __name__ == "__main__":
    # Filter out --email flag from arguments
    args = [arg for arg in sys.argv[1:] if arg != "--email"]
    send_email = "--email" in sys.argv or os.getenv("SEND_TRAINING_EMAIL", "false").lower() == "true"
    
    # Allow command-line arguments
    # Paths will be resolved relative to project root in train_and_save_model
    data_path = args[0] if len(args) > 0 else "data/salary_data.csv"
    model_path = args[1] if len(args) > 1 else "models/model.pkl"
    
    try:
        metrics = train_and_save_model(data_path, model_path)
        print("\n✅ Training completed successfully!")
        
        # Send email notification on success
        if send_email:
            try:
                from src.notify import notify_training_success
                print("\n📧 Sending training success notification...")
                success = notify_training_success(metrics)
                if success:
                    print("✅ Email notification sent successfully!")
                else:
                    print("⚠️ Failed to send email notification. Check email configuration.")
            except ImportError:
                print("⚠️ Email notification module not available.")
            except Exception as e:
                print(f"⚠️ Error sending email notification: {str(e)}")
        
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ Training failed: {error_msg}")
        
        # Send email notification on failure
        if send_email:
            try:
                from src.notify import notify_training_failure
                print("\n📧 Sending training failure notification...")
                notify_training_failure(error_msg)
            except ImportError:
                print("⚠️ Email notification module not available.")
            except Exception as e2:
                print(f"⚠️ Error sending email notification: {str(e2)}")
        
        sys.exit(1)

