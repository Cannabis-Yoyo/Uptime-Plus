import smtplib
import os
from email.mime.text import MIMEText


def send_email_alert(subject, message):
    sender = os.getenv("ALERT_EMAIL")
    password = os.getenv("ALERT_PASSWORD")
    recipient = os.getenv("ALERT_RECIPIENT")

    if not sender or not password or not recipient:
        return False

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
        return True
    except Exception:
        return False
