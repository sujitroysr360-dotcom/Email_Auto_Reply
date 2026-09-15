from gmail_auth import get_gmail_service
import base64
from email.mime.text import MIMEText


def send_email(to, subject, body):
    service = get_gmail_service()

    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject

    raw_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    message_body = {
        "raw": raw_message
    }

    service.users().messages().send(
        userId="me",
        body=message_body
    ).execute()

    print("Email sent successfully!")


if __name__ == "__main__":
    send_email(
        "roysujit2004@gmail.com",
        "Test Auto Reply",
        "Hello, this is an automated reply from Sujit's AI."
    )