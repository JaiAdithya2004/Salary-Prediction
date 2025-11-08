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


def notify_drift_detected(drift_report: dict) -> bool:
    """Send alert when data drift is detected."""
    title = "⚠️ Data Drift Detected in New Dataset"
    drifted = [k for k, v in drift_report.items() if "⚠️" in v]
    stable = [k for k, v in drift_report.items() if "✅" in v]
    body = f"""
    <p>Drift detected in {len(drifted)} feature(s): {', '.join(drifted)}</p>
    <p>Stable features: {', '.join(stable)}</p>
    <p>Retraining is recommended.</p>
    """
    return notify_email_html(title, body)


def notify_no_drift(drift_report: dict) -> bool:
    """Send info email if no drift found."""
    title = "✅ No Data Drift Detected"
    body = f"""
    <p>No drift detected in the latest dataset. All features remain stable.</p>
    <p>Checked {len(drift_report)} features.</p>
    """
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
