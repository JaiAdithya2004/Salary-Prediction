"""Data drift detection module with email notification support."""
import pandas as pd
import numpy as np
from scipy.stats import ks_2samp
import os
import sys
from typing import Tuple, Optional


def detect_data_drift(
    old_data_path: str,
    new_data_path: str,
    threshold: float = 0.05,
    send_email: bool = False,
    repo_name: str = "job-salary-predictor"
) -> Tuple[dict, bool]:
    """
    Detect data drift between old and new datasets.
    
    Args:
        old_data_path: Path to original training data
        new_data_path: Path to new data file
        threshold: P-value threshold for drift detection (default: 0.05)
        send_email: Whether to send email notification (default: False)
        repo_name: Repository name for email notifications
    
    Returns:
        tuple: (drift_report dict, drift_detected bool)
    """
    if not os.path.exists(old_data_path):
        print(f"⚠️ Old data file not found: {old_data_path}")
        return {}, False
    
    if not os.path.exists(new_data_path):
        print(f"⚠️ New data file not found: {new_data_path}")
        return {}, False
    
    old = pd.read_csv(old_data_path)
    new = pd.read_csv(new_data_path)
    
    drift_report = {}
    drift_detected = False
    
    # Detect drift in numeric columns
    numeric_cols = old.select_dtypes(include=[np.number]).columns
    numeric_cols = [col for col in numeric_cols if col not in ['Salary']]  # Exclude target
    
    for col in numeric_cols:
        if col in new.columns:
            try:
                stat, p_value = ks_2samp(old[col].dropna(), new[col].dropna())
                if p_value < threshold:
                    drift_report[col] = {
                        "status": "⚠️ Drift Detected",
                        "p_value": float(p_value),
                        "statistic": float(stat)
                    }
                    drift_detected = True
                else:
                    drift_report[col] = {
                        "status": "✅ Stable",
                        "p_value": float(p_value),
                        "statistic": float(stat)
                    }
            except Exception as e:
                drift_report[col] = {
                    "status": f"❌ Error: {str(e)}",
                    "p_value": None,
                    "statistic": None
                }
    
    # Check categorical distribution changes
    categorical_cols = old.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        if col in new.columns:
            old_dist = old[col].value_counts(normalize=True)
            new_dist = new[col].value_counts(normalize=True)
            
            # Calculate total variation distance
            all_categories = set(old_dist.index) | set(new_dist.index)
            tvd = sum(abs(old_dist.get(cat, 0) - new_dist.get(cat, 0)) for cat in all_categories) / 2
            
            if tvd > 0.2:  # Threshold for categorical drift
                drift_report[col] = {
                    "status": "⚠️ Drift Detected",
                    "tvd": float(tvd)
                }
                drift_detected = True
            else:
                drift_report[col] = {
                    "status": "✅ Stable",
                    "tvd": float(tvd)
                }
    
    print("\n🔍 Data Drift Detection Report:")
    print("=" * 50)
    for col, result in drift_report.items():
        print(f"{col}: {result['status']}")
        if 'p_value' in result and result['p_value'] is not None:
            print(f"  P-value: {result['p_value']:.4f}")
        if 'tvd' in result:
            print(f"  TVD: {result['tvd']:.4f}")
    print("=" * 50)
    
    # Send email notification if requested
    if send_email:
        try:
            from src.notify import notify_drift_detected, notify_no_drift
            
            print("\n📧 Sending email notification...")
            if drift_detected:
                success = notify_drift_detected(
                    drift_report=drift_report,
                    old_data_path=old_data_path,
                    new_data_path=new_data_path,
                    repo_name=repo_name
                )
                if success:
                    print("✅ Drift alert email sent successfully!")
                else:
                    print("⚠️ Failed to send drift alert email. Check email configuration.")
            else:
                # Send notification when no drift is detected (default: enabled)
                # Can be disabled by setting NOTIFY_ON_NO_DRIFT=false
                notify_on_no_drift = os.getenv("NOTIFY_ON_NO_DRIFT", "true").lower() == "true"
                if notify_on_no_drift:
                    success = notify_no_drift(
                        drift_report=drift_report,
                        new_data_path=new_data_path,
                        repo_name=repo_name
                    )
                    if success:
                        print("✅ No-drift notification sent successfully!")
                    else:
                        print("⚠️ Failed to send no-drift notification.")
                else:
                    print("ℹ️  No-drift notification disabled (NOTIFY_ON_NO_DRIFT=false)")
        except ImportError:
            print("⚠️ Email notification module not available. Install python-dotenv if needed.")
        except Exception as e:
            print(f"⚠️ Error sending email notification: {str(e)}")
    
    if drift_detected:
        print("\n⚠️ Data drift detected! Model retraining recommended.")
        return drift_report, True
    else:
        print("\n✅ No significant data drift detected.")
        return drift_report, False


def monitor_new_data(
    old_data_path: str = "data/salary_data.csv",
    new_data_dir: str = "data/new_data",
    check_interval: int = 60,
    threshold: float = 0.05,
    send_email: bool = True,
    repo_name: str = "job-salary-predictor"
):
    """
    Monitor directory for new data files and run drift detection automatically.
    
    Args:
        old_data_path: Path to original training data
        new_data_dir: Directory to monitor for new data files
        check_interval: Seconds between checks (default: 60)
        threshold: P-value threshold for drift detection
        send_email: Whether to send email notifications
        repo_name: Repository name for notifications
    """
    import time
    from datetime import datetime
    from pathlib import Path
    
    # Track processed files
    processed_files = set()
    
    print("\n" + "="*70)
    print("  DATA DRIFT MONITORING SYSTEM")
    print("="*70)
    print(f"\n📁 Monitoring directory: {new_data_dir}")
    print(f"📊 Reference data: {old_data_path}")
    print(f"⏱️  Check interval: {check_interval} seconds")
    print(f"🔍 Drift threshold: {threshold}")
    print(f"📧 Email notifications: {'Enabled' if send_email else 'Disabled'}")
    print("\n🔄 Starting monitoring... (Press Ctrl+C to stop)\n")
    
    # Ensure directory exists
    os.makedirs(new_data_dir, exist_ok=True)
    
    try:
        while True:
            # Check for CSV files in the monitored directory
            if os.path.exists(new_data_dir):
                for file in os.listdir(new_data_dir):
                    if file.endswith('.csv'):
                        file_path = os.path.join(new_data_dir, file)
                        file_stat = os.stat(file_path)
                        file_key = (file_path, file_stat.st_mtime)
                        
                        if file_key not in processed_files:
                            processed_files.add(file_key)
                            
                            print(f"\n{'='*70}")
                            print(f"🔍 New data detected: {file_path}")
                            print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                            print(f"{'='*70}\n")
                            
                            # Run drift detection
                            detect_data_drift(
                                old_data_path=old_data_path,
                                new_data_path=file_path,
                                threshold=threshold,
                                send_email=send_email,
                                repo_name=repo_name
                            )
                            
                            print(f"\n✅ Processing complete for: {file_path}\n")
            
            # Wait before next check
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoring stopped by user.")
        print("✅ Exiting gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error in monitoring loop: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Check if monitoring mode
    if "--monitor" in sys.argv:
        send_email = "--email" in sys.argv
        monitor_new_data(send_email=send_email)
    elif len(sys.argv) >= 3:
        # Normal drift detection mode
        old_path = sys.argv[1]
        new_path = sys.argv[2]
        send_email = "--email" in sys.argv
        
        detect_data_drift(old_path, new_path, send_email=send_email)
    else:
        print("Usage:")
        print("  python -m src.drift_detector <old_data_path> <new_data_path> [--email]")
        print("  python -m src.drift_detector --monitor [--email]")
        print("\nOptions:")
        print("  --email          Send email notification when drift is detected")
        print("  --monitor         Run continuous monitoring (watches data/new_data/)")
        print("\nExamples:")
        print("  python -m src.drift_detector data/salary_data.csv data/new_data/latest.csv")
        print("  python -m src.drift_detector data/salary_data.csv data/new_data/latest.csv --email")
        print("  python -m src.drift_detector --monitor --email")
        sys.exit(1)

