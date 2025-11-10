"""
Email notification utilities for ML model updates and monitoring.
Author: Jai Aditya
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# -------------------------------------------------------------------
# Core email function
# -------------------------------------------------------------------

def notify_email(
    message: str,
    subject: str = "ML Model Notification",
    to_email: Optional[str] = None,
    html: bool = False
) -> bool:
    """
    Send email notification using Gmail SMTP.
    Supports HTML and plain text formats.
    """

    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    email_from = os.getenv("EMAIL_FROM")
    email_password = os.getenv("EMAIL_PASSWORD")
    email_to = to_email or os.getenv("EMAIL_TO")

    if not all([email_from, email_password, email_to]):
        print("⚠️ Missing email credentials in environment (.env)")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = email_from
        msg["To"] = email_to
        msg["Subject"] = subject

        body = MIMEText(message, "html" if html else "plain")
        msg.attach(body)

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_from, email_password)
            server.send_message(msg)

        print(f"✅ Email sent successfully to {email_to}")
        return True

    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False


# -------------------------------------------------------------------
# HTML helper
# -------------------------------------------------------------------

def notify_email_html(title: str, body: str, subject: Optional[str] = None) -> bool:
    html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .header {{
                background-color: #0078D7;
                color: white;
                padding: 15px;
                text-align: center;
                border-radius: 6px 6px 0 0;
            }}
            .content {{
                padding: 20px;
                background-color: #f4f4f4;
                border-radius: 0 0 6px 6px;
            }}
        </style>
    </head>
    <body>
        <div class="header"><h2>{title}</h2></div>
        <div class="content">{body}</div>
        <p style="font-size:12px;color:#666;text-align:center;">
            Sent automatically by Job Salary Predictor System
        </p>
    </body>
    </html>
    """
    return notify_email(html, subject or title, html=True)


# -------------------------------------------------------------------
# High-level notification helpers
# -------------------------------------------------------------------

def notify_training_success(metrics: Optional[Dict] = None) -> bool:
    """Send success notification after model retraining."""
    title = "✅ Model Retraining Completed Successfully"
    body = "<p>The Job Salary Predictor model has been retrained and saved.</p>"
    if metrics:
        body += "<h4>Performance Metrics:</h4><ul>"
        for k, v in metrics.items():
            body += f"<li><strong>{k.upper()}:</strong> {v:.3f}</li>"
        body += "</ul>"
    return notify_email_html(title, body)


def notify_training_failure(error: str) -> bool:
    """Send failure notification when retraining fails."""
    title = "❌ Model Retraining Failed"
    body = f"""
    <p><strong>Error:</strong> {error}</p>
    <p>Please check training logs and rerun the pipeline.</p>
    """
    return notify_email_html(title, body)


def notify_drift_detected(
    drift_report: dict, 
    old_data_path: Optional[str] = None,
    new_data_path: Optional[str] = None,
    repo_name: Optional[str] = None
) -> bool:
    """Send alert when data drift is detected."""
    title = "⚠️ Data Drift Detected in New Dataset"
    
    # Handle both dict format (with 'status' key) and string format
    drifted = []
    stable = []
    for k, v in drift_report.items():
        if isinstance(v, dict):
            status = v.get('status', '')
            if "⚠️" in status or "Drift" in status:
                drifted.append(k)
            elif "✅" in status or "Stable" in status:
                stable.append(k)
        elif isinstance(v, str):
            if "⚠️" in v or "Drift" in v:
                drifted.append(k)
            elif "✅" in v or "Stable" in v:
                stable.append(k)
    
    body = f"""
    <p><strong>Drift detected in {len(drifted)} feature(s):</strong> {', '.join(drifted) if drifted else 'None'}</p>
    <p><strong>Stable features ({len(stable)}):</strong> {', '.join(stable) if stable else 'None'}</p>
    """
    
    if old_data_path:
        body += f"<p><strong>Reference data:</strong> {old_data_path}</p>"
    if new_data_path:
        body += f"<p><strong>New data:</strong> {new_data_path}</p>"
    
    body += "<p><strong>Action:</strong> Model retraining is recommended.</p>"
    
    return notify_email_html(title, body)


def notify_no_drift(
    drift_report: dict,
    new_data_path: Optional[str] = None,
    repo_name: Optional[str] = None
) -> bool:
    """Send info email if no drift found."""
    title = "✅ No Data Drift Detected"
    
    # Count stable features
    stable_count = 0
    feature_names = []
    for k, v in drift_report.items():
        if isinstance(v, dict):
            status = v.get('status', '')
            if "✅" in status or "Stable" in status:
                stable_count += 1
                feature_names.append(k)
        elif isinstance(v, str):
            if "✅" in v or "Stable" in v:
                stable_count += 1
                feature_names.append(k)
        else:
            stable_count += 1
            feature_names.append(k)
    
    body = f"""
    <p>No drift detected in the latest dataset. All features remain stable.</p>
    <p><strong>Checked {len(drift_report)} feature(s):</strong> {', '.join(feature_names[:10])}{'...' if len(feature_names) > 10 else ''}</p>
    """
    
    if new_data_path:
        body += f"<p><strong>Data file:</strong> {new_data_path}</p>"
    
    body += "<p>The model continues to perform well with the current data distribution.</p>"
    
    return notify_email_html(title, body)


# -------------------------------------------------------------------
# CLI Testing
# -------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        message = sys.argv[1]
        subject = sys.argv[2] if len(sys.argv) > 2 else "ML Notification"
        notify_email(message, subject)
    else:
        print("Usage:")
        print("  python -m src.notify 'Message text' 'Subject line'")
        print("Example:")
        print("  python -m src.notify 'Model retraining complete' 'Training Status'")
