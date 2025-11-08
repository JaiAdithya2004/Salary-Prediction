"""
Automated ML Pipeline - Runs when new data is detected.
Executes: drift_detector -> preprocess -> train_model -> evaluate -> notify
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configuration
OLD_DATA_PATH = "data/salary_data.csv"
NEW_DATA_DIR = "data/new_data"
NEW_DATA_FILE = os.path.join(NEW_DATA_DIR, "latest.csv")
MODEL_PATH = "models/model.pkl"
METRICS_PATH = "models/metrics.json"
SEND_EMAIL = os.getenv("SEND_TRAINING_EMAIL", "true").lower() == "true"


def run_drift_detection():
    """Step 1: Run drift detection."""
    print("\n" + "="*70)
    print("STEP 1: DATA DRIFT DETECTION")
    print("="*70)
    
    if not os.path.exists(NEW_DATA_FILE):
        print(f"⚠️  New data file not found: {NEW_DATA_FILE}")
        print("   Skipping drift detection...")
        return None, False
    
    if not os.path.exists(OLD_DATA_PATH):
        print(f"⚠️  Old data file not found: {OLD_DATA_PATH}")
        print("   Skipping drift detection...")
        return None, False
    
    try:
        from src.drift_detector import detect_data_drift
        
        drift_report, drift_detected = detect_data_drift(
            old_data_path=OLD_DATA_PATH,
            new_data_path=NEW_DATA_FILE,
            threshold=0.05,
            send_email=SEND_EMAIL
        )
        
        if drift_detected:
            print("\n⚠️  DRIFT DETECTED - Proceeding with retraining...")
        else:
            print("\n✅ NO DRIFT DETECTED - Proceeding with retraining anyway...")
        
        return drift_report, drift_detected
        
    except Exception as e:
        print(f"❌ Error in drift detection: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, False


def run_preprocessing():
    """Step 2: Run preprocessing (data is already preprocessed in train_model, but we can add analysis)."""
    print("\n" + "="*70)
    print("STEP 2: DATA PREPROCESSING")
    print("="*70)
    
    try:
        # Preprocessing is handled automatically in train_model.py via clean_data()
        # But we can run additional preprocessing analysis if needed
        print("✅ Preprocessing will be handled during training (automatic cleaning)")
        print("   - Missing value handling")
        print("   - Duplicate removal")
        print("   - Feature encoding (OneHotEncoder for categorical, StandardScaler for numeric)")
        return True
    except Exception as e:
        print(f"❌ Error in preprocessing: {str(e)}")
        return False


def merge_new_data():
    """Merge new data with existing data."""
    print("\n" + "="*70)
    print("STEP 2.5: MERGING NEW DATA")
    print("="*70)
    
    if not os.path.exists(NEW_DATA_FILE):
        print(f"⚠️  New data file not found: {NEW_DATA_FILE}")
        return False
    
    try:
        from src.utils import merge_new_data
        
        merge_new_data(
            old_data_path=OLD_DATA_PATH,
            new_data_path=NEW_DATA_FILE,
            clean_new_data=True
        )
        print("✅ Data merged successfully!")
        return True
    except Exception as e:
        print(f"❌ Error merging data: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_training():
    """Step 3: Train the model."""
    print("\n" + "="*70)
    print("STEP 3: MODEL TRAINING")
    print("="*70)
    
    try:
        from src.train_model import train_and_save_model
        
        metrics = train_and_save_model(
            data_path=OLD_DATA_PATH,
            model_path=MODEL_PATH,
            clean=True
        )
        
        print("✅ Model training completed successfully!")
        return metrics
        
    except Exception as e:
        print(f"❌ Error in training: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def run_evaluation(metrics):
    """Step 4: Evaluate model (already done in train_model, but we verify)."""
    print("\n" + "="*70)
    print("STEP 4: MODEL EVALUATION")
    print("="*70)
    
    if metrics is None:
        print("⚠️  No metrics available from training")
        return False
    
    try:
        # Metrics are already saved in train_model.py via evaluate_model()
        # Just verify they exist
        if os.path.exists(METRICS_PATH):
            with open(METRICS_PATH, 'r') as f:
                saved_metrics = json.load(f)
            print("✅ Evaluation metrics:")
            print(f"   MAE: {saved_metrics.get('mae', 'N/A'):.2f}")
            print(f"   R²: {saved_metrics.get('r2', 'N/A'):.3f}")
            print(f"   RMSE: {saved_metrics.get('rmse', 'N/A'):.2f}")
            return True
        else:
            print("⚠️  Metrics file not found")
            return False
            
    except Exception as e:
        print(f"❌ Error in evaluation: {str(e)}")
        return False


def send_notifications(metrics, drift_report=None, drift_detected=False):
    """Step 5: Send email notifications."""
    print("\n" + "="*70)
    print("STEP 5: SENDING NOTIFICATIONS")
    print("="*70)
    
    if not SEND_EMAIL:
        print("📧 Email notifications disabled (SEND_TRAINING_EMAIL=false)")
        return True
    
    try:
        from src.notify import notify_training_success
        
        success = notify_training_success(metrics)
        
        if success:
            print("✅ Training success notification sent!")
        else:
            print("⚠️  Failed to send notification")
        
        return success
        
    except Exception as e:
        print(f"⚠️  Error sending notification: {str(e)}")
        return False


def main():
    """Main pipeline execution."""
    print("\n" + "="*70)
    print("  AUTOMATED ML PIPELINE")
    print("="*70)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Project root: {PROJECT_ROOT}")
    print(f"📊 Old data: {OLD_DATA_PATH}")
    print(f"📊 New data: {NEW_DATA_FILE}")
    print(f"📧 Email notifications: {'Enabled' if SEND_EMAIL else 'Disabled'}")
    
    # Track results
    results = {
        "drift_detection": False,
        "preprocessing": False,
        "data_merge": False,
        "training": False,
        "evaluation": False,
        "notification": False
    }
    
    drift_report = None
    drift_detected = False
    metrics = None
    
    try:
        # Step 1: Drift Detection
        drift_report, drift_detected = run_drift_detection()
        results["drift_detection"] = True
        
        # Step 2: Preprocessing
        results["preprocessing"] = run_preprocessing()
        
        # Step 2.5: Merge new data (if new data exists)
        if os.path.exists(NEW_DATA_FILE):
            results["data_merge"] = merge_new_data()
        else:
            print("\n⚠️  No new data to merge, using existing data")
            results["data_merge"] = True
        
        # Step 3: Training
        metrics = run_training()
        results["training"] = metrics is not None
        
        if not results["training"]:
            print("\n❌ Pipeline failed at training step!")
            # Send failure notification
            if SEND_EMAIL:
                try:
                    from src.notify import notify_training_failure
                    notify_training_failure("Training failed in automated pipeline")
                except:
                    pass
            sys.exit(1)
        
        # Step 4: Evaluation
        results["evaluation"] = run_evaluation(metrics)
        
        # Step 5: Notifications
        results["notification"] = send_notifications(metrics, drift_report, drift_detected)
        
        # Summary
        print("\n" + "="*70)
        print("  PIPELINE SUMMARY")
        print("="*70)
        print(f"✅ Drift Detection: {'Success' if results['drift_detection'] else 'Skipped'}")
        print(f"✅ Preprocessing: {'Success' if results['preprocessing'] else 'Failed'}")
        print(f"✅ Data Merge: {'Success' if results['data_merge'] else 'Failed'}")
        print(f"✅ Training: {'Success' if results['training'] else 'Failed'}")
        print(f"✅ Evaluation: {'Success' if results['evaluation'] else 'Failed'}")
        print(f"✅ Notification: {'Success' if results['notification'] else 'Failed'}")
        
        if all([results["training"], results["evaluation"]]):
            print("\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")
            print(f"📁 Model saved to: {MODEL_PATH}")
            print(f"📊 Metrics saved to: {METRICS_PATH}")
            sys.exit(0)
        else:
            print("\n⚠️  Pipeline completed with some failures")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error in pipeline: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Send failure notification
        if SEND_EMAIL:
            try:
                from src.notify import notify_training_failure
                notify_training_failure(f"Pipeline failed: {str(e)}")
            except:
                pass
        
        sys.exit(1)


if __name__ == "__main__":
    main()

