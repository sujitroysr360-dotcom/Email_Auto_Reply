from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import base64

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
TOKEN_FILE = "token.json"


def get_gmail_service():
    creds = Credentials.from_authorized_user_file(
        TOKEN_FILE,
        SCOPES
    )

    return build(
        "gmail",
        "v1",
        credentials=creds
    )


def get_email_body(payload):
    import base64
    from bs4 import BeautifulSoup

    # First look for HTML version
    if "parts" in payload:

        for part in payload["parts"]:

            if part["mimeType"] == "text/html":
                data = part["body"].get("data")

                if data:
                    html = base64.urlsafe_b64decode(
                        data
                    ).decode("utf-8", errors="ignore")

                    return BeautifulSoup(
                        html,
                        "html.parser"
                    ).get_text(
                        "\n",
                        strip=True
                    )

        # If no HTML found, look for plain text
        for part in payload["parts"]:

            if part["mimeType"] == "text/plain":
                data = part["body"].get("data")

                if data:
                    return base64.urlsafe_b64decode(
                        data
                    ).decode("utf-8", errors="ignore")

        # Check nested parts
        for part in payload["parts"]:

            if "parts" in part:
                result = get_email_body(part)

                if result:
                    return result

    else:
        data = payload["body"].get("data")

        if data:
            return base64.urlsafe_b64decode(
                data
            ).decode("utf-8", errors="ignore")

    return ""


def read_emails():
    service = get_gmail_service()

    results = service.users().messages().list(
        userId="me",
        labelIds=["INBOX"],
        maxResults=5
    ).execute()

    messages = results.get("messages", [])

    if not messages:
        print("No emails found.")
        return

    print(f"\nFound {len(messages)} email(s):\n")

    for message in messages:

        email = service.users().messages().get(
            userId="me",
            id=message["id"],
            format="full"
        ).execute()

        headers = email["payload"]["headers"]

        sender = "Unknown"
        subject = "No Subject"

        for header in headers:
            if header["name"] == "From":
                sender = header["value"]

            elif header["name"] == "Subject":
                subject = header["value"]

        body = get_email_body(email["payload"])

        print("--------------------------------")
        print("From   :", sender)
        print("Subject:", subject)
        print("Body   :")
        print(body[:1000])
        print()


if __name__ == "__main__":
    read_emails()