from gmail_auth import get_gmail_service
from gmail_sender import send_email
import base64
import sqlite3
from datetime import datetime
from allowed_senders import is_allowed_sender


DATABASE = "database/email.db"


def get_header(headers, name):
    for header in headers:
        if header["name"].lower() == name.lower():
            return header["value"]

    return ""


def get_email_body(payload):
    body = ""

    if "body" in payload and payload["body"].get("data"):
        body = base64.urlsafe_b64decode(
            payload["body"]["data"]
        ).decode("utf-8", errors="ignore")

    elif "parts" in payload:

        for part in payload["parts"]:
            body = get_email_body(part)

            if body:
                break

    return body


def update_statistics(
    emails_checked=0,
    replies_sent=0,
    emails_skipped=0,
    last_check=None
):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE statistics
        SET
            emails_checked = emails_checked + ?,
            replies_sent = replies_sent + ?,
            emails_skipped = emails_skipped + ?,
            last_check = COALESCE(?, last_check)
        WHERE id = 1
    """, (
        emails_checked,
        replies_sent,
        emails_skipped,
        last_check
    ))

    conn.commit()
    conn.close()


def auto_reply():

    service = get_gmail_service()

    results = service.users().messages().list(
        userId="me",
        q="is:unread -from:me"
    ).execute()

    messages = results.get("messages", [])

    print(f"Found {len(messages)} unread email(s).")

    for message in messages:

        msg = service.users().messages().get(
            userId="me",
            id=message["id"],
            format="full"
        ).execute()

        payload = msg["payload"]
        headers = payload.get("headers", [])

        sender = get_header(headers, "From")
        subject = get_header(headers, "Subject")
        body = get_email_body(payload)

        print("\n-----------------------------")
        print("From:", sender)
        print("Subject:", subject)
        print("Body:", body[:500])

        # Extract email address
        if "<" in sender and ">" in sender:
            sender_email = sender.split("<")[1].split(">")[0]
        else:
            sender_email = sender

        sender_email = sender_email.lower().strip()

        # Count this email as checked
        update_statistics(
            emails_checked=1
        )

        # Check allowed sender
        if not is_allowed_sender(sender_email):

            print("Skipped:", sender_email)

            update_statistics(
                emails_skipped=1
            )

            continue

        # Create reply
        reply_subject = "Re: " + subject

        reply_body = (
            "Hello,\n\n"
            "Thank you for your email. "
            "This is an automatic reply from my AI assistant.\n\n"
            "I will get back to you soon.\n\n"
            "Regards,\n"
            "Sujit Roy"
        )

        # Send reply
        send_email(
            sender_email,
            reply_subject,
            reply_body
        )

        update_statistics(
            replies_sent=1
        )

        # Mark email as read
        service.users().messages().modify(
            userId="me",
            id=message["id"],
            body={
                "removeLabelIds": ["UNREAD"]
            }
        ).execute()

        print("Automatic reply sent!")

    # Update last check time
    current_time = datetime.now().strftime(
        "%d %b %Y, %I:%M:%S %p"
    )

    update_statistics(
        last_check=current_time
    )

    print("\nStatistics updated successfully!")


if __name__ == "__main__":
    auto_reply()