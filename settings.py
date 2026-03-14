import os

from dotenv import load_dotenv

load_dotenv()

DISPLAY_NAME = os.getenv("display_name")
SENDER_EMAIL = os.getenv("sender_email")
PASSWORD = os.getenv("password")
MAIL_COMPOSE: str = os.getenv("mail_compose", "compose.html")

if os.path.exists("subject.txt"):
    with open("subject.txt", "r", encoding="utf-8") as f:
        SUBJECT = f.read().strip()
else:
    SUBJECT: str | None = os.getenv("subject", None)

try:
    assert DISPLAY_NAME
    assert SENDER_EMAIL
    assert PASSWORD
    assert MAIL_COMPOSE
except AssertionError:
    print("Please set up credentials. Read https://github.com/aahnik/automailer#usage")
else:
    print("Credentials loaded successfully")
    print(f"Template path: {MAIL_COMPOSE}")
    print(f"Subject: {SUBJECT if SUBJECT else '(Auto-generated from template)'}")
    # Masking email for safety while still providing debug info
    if SENDER_EMAIL:
        parts = SENDER_EMAIL.split("@")
        masked_email = f"{parts[0][:2]}***@{parts[1]}" if len(parts) > 1 else "***"
        print(f"Sender: {masked_email}")
