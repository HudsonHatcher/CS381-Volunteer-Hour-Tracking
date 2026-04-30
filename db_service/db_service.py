import socket
import hashlib
import threading
import sqlite3

HOST = "db_service"
PORT = 5001

import json

def send_json(sock, data):
    message = json.dumps(data).encode()
    sock.sendall(message)

def recv_json(con):
    data = con.recv(4096)
    return json.loads(data.decode())

# Initialize database
conn = sqlite3.connect("/app/data/volunteer.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS people (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT UNIQUE,
    password TEXT NOT NULL,
    organization TEXT,
    hours INTEGER NOT NULL,
    pending INTEGER NOT NULL,
    status TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    hours INTEGER NOT NULL,
    status TEXT DEFAULT 'pending'
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS organizations (
    organization TEXT PRIMARY KEY,
    supervisor_email TEXT NOT NULL,
    tot_hours INTEGER NOT NULL
)
""")
conn.commit()


def handle_client(con):
    try:
        request = recv_json(con)

        #Org I/O Request
        if request["action"] == "jOrg":
            cursor.execute(
                "SELECT organization FROM organizations WHERE organization=?", (request["org"],)
            )
            org = cursor.fetchone()
            if org:
                cursor.execute(
                    "UPDATE people SET organization=?, status=? WHERE id=?", (request["org"], "member", request["id"])
                )
                conn.commit()
                send_json(con, {"status": "member"})
            else:
                send_json(con, {"err": "mOrg"})

        elif request["action"] == "cOrg":
            cursor.execute(
                "SELECT organization FROM organizations WHERE organization=?", (request["org"],)
            )
            org = cursor.fetchone()
            if org:
                send_json(con, {"err": "eOrg"})
            else:
                cursor.execute(
                    "INSERT INTO organizations (organization, supervisor_email, tot_hours) VALUES (?, ?, 0)", (request["org"], request["em"])
                )
                cursor.execute(
                    "UPDATE people SET organization=?, status=? WHERE id=?", (request["org"], "leader", request["id"])
                )
                conn.commit()
                send_json(con, {"status": "leader"})
        elif request["action"] == "listm":
            cursor.execute(
                "SELECT organization FROM people WHERE id=?", (request["id"],)
            )
            org = cursor.fetchone()
            if org:
                cursor.execute(
                    "SELECT user, id FROM people WHERE organization=?", (org[0],)
                )
                rows = cursor.fetchall()
                if rows:
                    send_json(con, {"data": rows})

        elif request["action"] == "store":
            #Pass Email and Specefic id To Email Service
            cursor.execute(
                "SELECT organization, pending, user FROM people WHERE id=?", (request["userid"],)
            )
            org = cursor.fetchone()
            if org:
                #Add to Entries
                cursor.execute(
                    "INSERT INTO entries (user, hours) VALUES (?, ?) RETURNING id",
                    (org[2], request["hours"])
                )
                id = cursor.fetchone()[0]
                conn.commit()

                #Email Organization Leader
                cursor.execute("SELECT supervisor_email FROM organizations WHERE organization=?", (org[0],))
                email = cursor.fetchone()[0]
                emCon = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                emCon.connect(("email_service", 5002))

                send_json(emCon, {"email": email, "id": id})
                emCon.close()
                send_json(con, {"status": "stored"})

                #Add To Pending Hours
                totPend = request["hours"] + org[1]
                cursor.execute("UPDATE people SET pending=? WHERE id=?", (totPend, request["userid"]))
                conn.commit()
                return
            send_json(con, {"err": "nOrg"})

        elif request["action"] == "get":
            cursor.execute("SELECT * FROM people WHERE id=?", (request["id"],))
            rows = cursor.fetchall()
            if rows:
                cursor.execute("SELECT * FROM organizations WHERE organization=?", (rows[0][3],))
                rows2 = cursor.fetchall()
                if rows2:
                    send_json(con, {"userData": rows, "orgData": rows2})
            else:
                send_json(con, {"err": "noSuchMember"})

        elif request["action"] == "updE":
            cursor.execute(
                "SELECT organization FROM people WHERE id=?", (request["id"],)
            )
            org = cursor.fetchone()
            if org:
                cursor.execute(
                    "UPDATE organizations SET supervisor_email=? WHERE organization=?", (request["email"], org[0])
                )
                conn.commit()
                #Send Success
                send_json(con, {"status": "complete"})

        elif request["action"] == "updU":
            cursor.execute(
                "SELECT organization FROM people WHERE id=?", (request["id"],)
            )
            org1 = cursor.fetchone()
            if org1:
                cursor.execute(
                    "SELECT organization FROM people WHERE id=?", (request["Uid"],)
                )
                org2 = cursor.fetchone()
                if org2 and org1[0] == org2[0]:
                    cursor.execute(
                        """UPDATE people SET status="leader" WHERE id=?""", (request["Uid"],)
                    )
                    conn.commit()
                    #Send Success
                    send_json(con, {"status": "complete"})

        elif request["action"] == "storeU":
            cursor.execute(
                "SELECT organization FROM people WHERE id=?", (request["id"],)
            )
            org1 = cursor.fetchone()
            if org1:
                cursor.execute(
                    "SELECT organization FROM people WHERE id=?", (request["Uid"],)
                )
                org2 = cursor.fetchone()
                if org2 and org1[0] == org2[0]:
                    #Pass Email and Specefic id To Email Service
                    cursor.execute(
                        "SELECT organization, pending, user FROM people WHERE id=?", (request["Uid"],)
                    )
                    org = cursor.fetchone()
                    if org:
                        #Add to Entries
                        cursor.execute(
                            "INSERT INTO entries (user, hours) VALUES (?, ?) RETURNING id",
                            (org[2], request["hours"])
                        )
                        id = cursor.fetchone()[0]
                        conn.commit()

                        #Email Organization Leader
                        cursor.execute("SELECT supervisor_email FROM organizations WHERE organization=?", (org[0],))
                        email = cursor.fetchone()[0]
                        emCon = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        emCon.connect(("email_service", 5002))

                        send_json(emCon, {"email": email, "id": id})
                        emCon.close()
                        print("Fuck")
                        send_json(con, {"status": "stored"})

                        #Add To Pending Hours
                        totPend = request["hours"] + org[1]
                        cursor.execute("UPDATE people SET pending=? WHERE id=?", (totPend, request["Uid"]))
                        conn.commit()
                        return
            print("shit")
            send_json(con, {"err": "nOrg"})

        #Email Confirmation Goes Through
        elif request["action"] == "update":
            cursor.execute(
                "SELECT id, user, hours FROM entries WHERE id=?",
                (request.get("id"),)
            )
            ent = cursor.fetchone()

            cursor.execute(
                "SELECT user, hours, pending, organization FROM people WHERE user=?",
                (ent[1],)
            )
            userData = cursor.fetchone()

            if request["ver"] == "Y":
                newTotal = userData[1] + ent[2]
                newPending = userData[2] - ent[2]

                cursor.execute(
                    "UPDATE people SET hours=?, pending=? WHERE user=?",
                    (newTotal, newPending, ent[1])
                )

                cursor.execute(
                    "SELECT tot_hours FROM organizations WHERE organization=?",
                    (userData[3],)
                )
                orgData = cursor.fetchone()
                newOrgTotal = orgData[0] + ent[2]

                cursor.execute(
                    "UPDATE organizations SET tot_hours=? WHERE organization=?",
                    (newOrgTotal, userData[3])
                )

                cursor.execute(
                    "DELETE FROM entries WHERE id=?",
                    (request.get("id"),)
                )
                conn.commit()
            else:
                newPending = userData[2] - ent[2]

                cursor.execute(
                    "UPDATE people SET pending=? WHERE user=?",
                    (newPending, ent[1])
                )

                cursor.execute(
                    "DELETE FROM entries WHERE id=?",
                    (request.get("id"),)
                )
                conn.commit()

        elif request["action"] == "log" or request["action"] == "sign":
            if request["action"] == "sign":
                cursor.execute("SELECT id FROM people WHERE user=?", (request.get("username"),))
                i = cursor.fetchone()
                if i is None:
                    #Hash Password For Database Security
                    j = request["username"]
                    passw = request["password"]
                    code = int.from_bytes(j.encode('utf-8'), byteorder='big')
                    salt = (code) * ((code) / 2)
                    hasher = hashlib.sha256()
                    hasher.update(str(salt).encode())
                    hasher.update(passw.encode())
                    hPass = hasher.hexdigest()
                    print(hPass)
                    cursor.execute("INSERT INTO people (user, password, hours, pending) VALUES (?, ?, 0, 0)", (j, hPass))
                    conn.commit()
                else:
                    send_json(con, {"err": "uTkn"})
                    return

            #Log In After Signup or Just Log In
            cursor.execute("SELECT password, id, status FROM people WHERE user=?", (request.get("username"),))
            passw = cursor.fetchone()
            if passw is not None:
                i = passw[1]
                j = request["username"]
                code = int.from_bytes(j.encode('utf-8'), byteorder='big')
                salt = (code) * ((code) / 2)
                hasher = hashlib.sha256()
                hasher.update(str(salt).encode())
                hasher.update(request["password"].encode())
                hPass = hasher.hexdigest()
                if hPass == passw[0]:
                    stt = passw[2]
                    send_json(con, {"id": i, "status": stt})
                else:
                    send_json(con, {"err": "incLogin"})
            else:
                send_json(con, {"err": "notFnd"})

    except Exception as e:
        send_json(con, {"err": str(e)})
        pass

if __name__ == "__main__":
    # Connect
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.bind(('0.0.0.0', PORT))
    client.listen()
    con, addr = client.accept()

    #Listen and Respond Until Closed
    while True:
        handle_client(con)
        print(f"Something happened")