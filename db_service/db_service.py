import socket
import threading
import sqlite3

HOST = "db_service"
PORT = 5001

import json

def send_json(sock, data):
    message = json.dumps(data).encode()
    sock.sendall(message)

def recv_json(sock):
    data = sock.recv(4096)
    return json.loads(data.decode())

# Initialize database
conn = sqlite3.connect("volunteer.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    organization TEXT,
    hours INTEGER,
    supervisor_email TEXT,
    status TEXT
)
""")
conn.commit()


def handle_client(client):
    try:
        request = recv_json(client)

        if request["action"] == "store":
            cursor.execute(
                "INSERT INTO entries (user, organization, hours, supervisor_email, status) VALUES (?, ?, ?, ?, ?)",
                (request["user"], request["organization"], request["hours"], request["email"], "Pending")
            )
            conn.commit()
            send_json(client, {"status": "stored"})

        elif request["action"] == "get":
            cursor.execute("SELECT * FROM entries WHERE user=?", (request["user"],))
            rows = cursor.fetchall()
            send_json(client, {"data": rows})

        elif request["action"] == "update":
            cursor.execute(
                "UPDATE entries SET status=? WHERE id=?",
                (request["status"], request["id"])
            )
            conn.commit()
            send_json(client, {"status": "updated"})

    except Exception as e:
        send_json(client, {"error": str(e)})

    finally:
        client.close()

