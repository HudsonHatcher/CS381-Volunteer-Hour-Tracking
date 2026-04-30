import socket
import json
import smtplib
from email.mime.text import MIMEText

HOST = "0.0.0.0"
PORT = 5002

UI_BASE_URL = "http://localhost:5000/approve"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "jlsanders2006@gmail.com"
SMTP_PASS = "mphj cnis ttie goey"


def send_email(to_email, entry_id):
    approval_link = f"{UI_BASE_URL}?entry_id={entry_id}"

    body = f"""
    A volunteer has submitted hours.

    Click below to approve:
    {approval_link}

    """

    msg = MIMEText(body)
    msg["Subject"] = "Volunteer Hours Approval Required"
    msg["From"] = SMTP_USER
    msg["To"] = to_email

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)


def handle_client(conn):
    try:
        data = json.loads(conn.recv(4096).decode())
        email = data["email"]
        entry_id = data["id"]

        send_email(email, entry_id)

        conn.send(json.dumps({"status": "sent"}).encode())

    except Exception as e:
        conn.send(json.dumps({"err": str(e)}).encode())


if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print("Email service running...")

    while True:
        conn, _ = server.accept()
        handle_client(conn)
        conn.close()