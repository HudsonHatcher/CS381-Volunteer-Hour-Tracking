#Import Dependencies
from flask import Flask, render_template, request
from threading import Timer
import webbrowser
import json
import socket
import os

#User Id For Get Request (Start As None)
id = -1
stat = 0
con = True
usern = ""

#Make Template directory for flask processing
try:
    os.mkdir('templates')
except FileExistsError:
    pass

#Preset HTML Documents
dashboard = """
<!DOCTYPE html>
<html>
<style>
.main {
padding-top: 60px;
padding-left: 25px;
}
button {
 position: relative;
 display: inline-block;
 cursor: pointer;
 outline: none;
 border: 0;
 vertical-align: middle;
 text-decoration: none;
 font-family: inherit;
 font-size: 15px;
 margin-bottom: 5px;
}

button.learn-more {
 font-weight: 600;
 color: #382b22;
 text-transform: uppercase;
 padding: 1.25em 2em;
 background: #fff0f0;
 border: 2px solid #b18597;
 border-radius: 0.75em;
 -webkit-transform-style: preserve-3d;
 transform-style: preserve-3d;
 -webkit-transition: background 150ms cubic-bezier(0, 0, 0.58, 1), -webkit-transform 150ms cubic-bezier(0, 0, 0.58, 1);
 transition: transform 150ms cubic-bezier(0, 0, 0.58, 1), background 150ms cubic-bezier(0, 0, 0.58, 1), -webkit-transform 150ms cubic-bezier(0, 0, 0.58, 1);
}

button.learn-more::before {
 position: absolute;
 display: none;
 content: '';
 width: 100%;
 height: 100%;
 top: 0;
 left: 0;
 right: 0;
 bottom: 0;
 background: #f9c4d2;
 border-radius: inherit;
 transform: translate3d(0, 0.75em, -1em);
 transition: transform 150ms cubic-bezier(0, 0, 0.58, 1), box-shadow 150ms cubic-bezier(0, 0, 0.58, 1), -webkit-transform 150ms cubic-bezier(0, 0, 0.58, 1), -webkit-box-shadow 150ms cubic-bezier(0, 0, 0.58, 1);
}

button.learn-more:hover {
 background: #ffe9e9;
 -webkit-transform: translate(0, 0.25em);
 transform: translate(0, 0.25em);
}

button.learn-more:hover::before {
 -webkit-transform: translate3d(0, 0.5em, -1em);
 transform: translate3d(0, 0.5em, -1em);
}

button.learn-more:active {
 background: #ffe9e9;
 -webkit-transform: translate(0em, 0.75em);
 transform: translate(0em, 0.75em);
}

button.learn-more:active::before {
 -webkit-transform: translate3d(0, 0, -1em);
 transform: translate3d(0, 0, -1em);
}

.err {
font-weight: normal;
font-size:15px;
color: red;
opacity: 0.5;
padding-top: 0px;
margin: 0px;
}
.login {
position: relative;
display: {{ panelUp }};
margin: 0 auto;
border: 5px solid black;
border-radius: 15px;
justify-content: center;
align-items: center;
place-items: center;
background-color: #ff9eda;
height: 50vh;
width: 50vw;
z-index: 30;
}
.xBut {
position: absolute;
border-radius: 15px;
border: none;
width: 50px;
height: 50px;
font-size: 24px;
top: 0;
right: 0;
background-color: #ff9eda;
}
.wall {
display: {{ panelUp }};
background: rgba(256, 256, 256, 0.5);
position: absolute;
top:0;
left:0;
height: 99vh;
width: 99vw;
z-index: 20
}
.orgForms {
display: flex;
align-items: center;
flex-direction: row;
place-items: center;
gap: 1vw;
}

.form {
  display: flex;
  width: 20vw;
  height: 10vw;
  flex-direction: column;
  gap: 10px;
  background-color: white;
  padding: 2.5em;
  border-radius: 25px;
  transition: .4s ease-in-out;
  box-shadow: rgba(0, 0, 0, 0.4) 1px 2px 2px;
}

.form:hover {
  transform: translateX(-0.5em) translateY(-0.5em);
  border: 1px solid #171717;
  box-shadow: 10px 10px 0px #666666;
}

.heading {
  color: black;
  padding-bottom: 2em;
  text-align: center;
  font-weight: bold;
}

.input {
  border-radius: 5px;
  border: 1px solid whitesmoke;
  background-color: whitesmoke;
  outline: none;
  padding: 0.7em;
  transition: .4s ease-in-out;
}

.input:hover {
  box-shadow: 6px 6px 0px #969696,
             -3px -3px 10px #ffffff;
}

.input:focus {
  background: #ffffff;
  box-shadow: inset 2px 5px 10px rgba(0,0,0,0.3);
}

.form .btn {
  margin-top: 2em;
  align-self: center;
  padding: 0.7em;
  padding-left: 1em;
  padding-right: 1em;
  border-radius: 10px;
  border: none;
  color: black;
  transition: .4s ease-in-out;
  box-shadow: rgba(0, 0, 0, 0.4) 1px 1px 1px;
}

.form .btn:hover {
  box-shadow: 6px 6px 0px #969696,
             -3px -3px 10px #ffffff;
  transform: translateX(-0.5em) translateY(-0.5em);
}

.form .btn:active {
  transition: .2s;
  transform: translateX(0em) translateY(0em);
  box-shadow: none;
}
</style>
<head><title>Hour Submission</title></head>
<body>
    <button type="button" style="width: 50px; height: 50px;" onclick="openLog()">Login Screen</button>
    <div class=main>
        <form method='GET' action='/submit_hour'>
            <p style="margin: 0.5px;">
                <label>Volunteer Hours:
                <input type="text" id="hourSub" name="hourSub", placeholder="Enter a #">
                </input></label>
                <p class="err">{{ myErr }}</p>
            </p>
            <button type="submit" style="margin-top: 5px; padding=0.5px;")">Submit</button>
        </form>
    </div>
<div class="wall" id="login_wall"></div>
<div class="login" id="login_panel">
    <button type="button" onclick="closeLog()" class="xBut">X</button>
    {% if id < 0 %}
    <h1 style="text-size:24px;" id=headerPan>Login</h1>
    <form method='POST' action='login_req' id=loginForm>
        <p style="padding-top: 5vh;">
        <label style="text-size: 18px;">Username:</label><br>
        <input type="text" id="username" name="username" style="border: black; height: 25px; width: 50vh; border-radius: 15px;" placeholder=" username">
        </p>
        <label style="text-size: 18px; padding-top: 5vh;">Password:</label><br>
        <input type="password" id="password" name="password" style="border: black; height: 25px; width: 50vh; border-radius: 15px;" placeholder=" password"><br>
        <p style="padding-top: 1vh;">
        <button type="submit" style="top-margin: 15px;">Login</button>
        <button type="button" style="right-padding: 5px;" onclick="signupPut()">Sign Up</button>
        </p>
    </form>
    <form method='POST' action='sign_req' id=signForm style="display: none; pointer-events: none;">
        <p style="padding-top: 5vh;">
        <label style="text-size: 18px;">Username:</label><br>
        <input type="text" id="susername" name="username" style="border: black; height: 25px; width: 50vh; border-radius: 15px;" placeholder=" username">
        </p>
        <label style="text-size: 18px; margin-top: 5vh;">Password:</label><br>
        <input type="password" id="spassword" name="password" style="border: black; height: 25px; width: 50vh; border-radius: 15px;" placeholder=" password"><br>
        <label style="text-size: 18px; margin-top: 8vh;">Confirm Password:</label><br>
        <input type="password" id="conf" name="conf" style="border: black; height: 25px; width: 50vh; border-radius: 15px;" placeholder=" retype your password"><br>
        <p style="padding-top: 5px;">
        {% if con == False %}<span class="err" style="color: #4D1102;">Passwords Didn't Match!</span><br>{% endif %}
        <button type="submit" style="top-margin: 15px;">Sign Up</button>
        <button type="button" style="right-padding: 5px;" onclick="signPop()">Login</button>
        </p>
    </form>
    {% elif stat == 0 %}
        <h1 style="text-size:24px;" id=yli>{{ myHello }}</h1>
        <div class="orgForms">
        <form class="form" action='orgReq' method='GET'>
            <p class="heading">Join an Organization</p>
            <input class="input" placeholder="Enter your Organization Name" type="text" name="oName"> 
            <button class="btn" type="submit">Submit</button>
        </form>
        <form class="form" action='orgReq' method='POST'>
            <p class="heading">Create an Organization</p>
            <input class="input" placeholder="Enter your Email" type="text" name="email">
            <input class="input" placeholder="Enter your Organization Name" type="text" name="oName"> 
            <button class="btn" type="submit">Submit</button>
        </form>
        </div>
        {{ orgError }}
    {% elif stat == 1 %}
        <h1 style="text-size:24px;">{{ myHello }}<br>You Are a Member of Your Organization!</h1>
        <form action='reqi' method='GET'>
            <button class="learn-more" type=submit>Get Info!</button>
        </form>
        <div style="padding-top: 20px;">{{ killMe | safe }}</div>
    {% endif %}
</div>
</body>
<script>
function openLog() {
    const panel = document.getElementById("login_panel");
    panel.style.display = "block";
    const wall = document.getElementById("login_wall");
    wall.style.display = "block";
}
function closeLog() {
    const panel = document.getElementById("login_panel");
    panel.style.display = "none";
    const wall = document.getElementById("login_wall");
    wall.style.display = "none";
}
function signupPut() {
    const log = document.getElementById("loginForm");
    log.style.display = "none";
    log.style.pointerEvents = "none";
    const sig = document.getElementById("signForm");
    sig.style.display = "block";
    sig.style.pointerEvents = "auto";
    const head = document.getElementById("headerPan");
    head.innerHTML="Sign Up";
}
function signPop() {
    const log = document.getElementById("loginForm");
    log.style.display = "block";
    log.style.pointerEvents = "auto";
    const sig = document.getElementById("signForm");
    sig.style.display = "none";
    sig.style.pointerEvents = "none";
    const head = document.getElementById("headerPan");
    head.innerHTML="Log In";
}
</script>
</html>
"""

#Setup Flask For Request Handling
app = Flask(__name__)
#Write Presets To Templates Directory
with open("templates/index.html", "w") as file:
    file.write(dashboard)

#Open Browser
def openDash():
    webbrowser.open_new('http://127.0.0.1:5000')

#Flask Routing and Request Management
@app.route('/')
def homepage():
    return render_template('index.html', panelUp='none', id=id, stat=stat, myHello=f"Hello {usern}! How Can I Assist?")

@app.route('/reqi')
def getInfo():
    global id
    userid = id
    print(userid)
    dataStr = f"{{\"action\": \"get\", \"id\": \"{userid}\"}}"
    dataClient.send(dataStr.encode('utf-8'))
    data = json.loads(dataClient.recv(4096).decode())
    outStr = ""

    if data.get("err"):
        print(data["err"])
        return render_template('index.html', panelUp='block', id=id, stat=stat, myHello=f"Failed to Fetch")
    else:
        #Build Info Output in HTML
        outStr = """<div class = orgForms><div style="display: flex; width: 20vw; height: auto; flex-direction: column; justify-content: center;"><h1 style="font-size: 24px;">User Information:</h1>"""
        ind = ['User Id', 'Username', 'PassHash', '', 'Hours', 'Pending Hours', 'Status']
        lis = data["userData"]
        for i, item in enumerate(lis[0]):
            if i == 3:
                continue
            else:
                stri = f"<p style=\"font-size: 16px; margin-top:10px; margin-bottom: 0px;\"><b>{ind[i]}:</b><br>{item}</p>"
                outStr = outStr + stri
        outStr = outStr + """</div><div style="display: flex; width: 20vw; height: auto; flex-direction: column;"><h1 style="font-size:24px;">Organization Information:</h1>"""

        ind = ['Org Name', 'Leader\'s Email', 'Total Verified Hours']
        lis = data["orgData"]
        for i, item in enumerate(lis[0]):
            stri = f"<p style=\"font-size: 16px; margin-top:10px; margin-bottom: 0px;\"><b>{ind[i]}:</b><br>{item}</p>"
            outStr = outStr + stri
        outStr = outStr + """</div></div>"""

    return render_template('index.html', panelUp='block', id=id, stat=stat, myHello=f"Information Fetched", killMe=outStr)

@app.route('/submit_hour')
def submission():
    val = request.args['hourSub']
    #Verify That Request is A Number
    digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    for c in list(val):
        if c not in digits:
            return render_template('index.html', myErr='Please Enter a Number', panelUp='none', id=id, stat=stat, myHello=f"Hello {usern}! How Can I Assist?")
    #Clear Leading Zeros
    val = val.lstrip('0')
    
    dataStr = f"{{\"action\": \"store\", \"hours\": {val}, \"userid\": {id}}}"
    #Pass Integer Hour Submission to Database Handler
    dataClient.send(dataStr.encode('utf-8'))
    data = json.loads(dataClient.recv(4096).decode())
    if data.get("err"):
        print(data["err"])
    return render_template('index.html', panelUp='none', id=id, stat=stat, myHello=f"Hello {usern}! How Can I Assist?")

@app.route('/orgReq', methods=['GET', 'POST'])
def orgReq():
    global id
    global stat
    userid = id
    name = request.form.get('oName')
    dataStr = ""

    if request.method == 'GET':
        name = request.args.get('oName')
        dataStr = f'{{\"action\": \"jOrg\", \"id\": \"{userid}\", \"org\": \"{name}\"}}'
    if request.method == 'POST':
        name = request.form.get('oName')
        servE = request.form.get('email')
        dataStr = f'{{\"action\": \"cOrg\", \"id\": \"{userid}\", \"org\": \"{name}\", \"em\": \"{servE}\"}}'
    dataClient.send(dataStr.encode('utf-8'))
    data = json.loads(dataClient.recv(4096).decode())
    if data.get("err"):
        print(data["err"])
        return render_template('index.html', panelUp='block', id=id, stat=stat, myHello=f"Hello {usern}! How Can I Assist?")
    match (data["status"]):
        case ('member'): 
            stat = 1
        case ('leader'):
            stat = 2
        case _:
            stat = 0
    return render_template('index.html', panelUp='block', id=id, stat=stat, myHello=f"Hello {usern}! How Can I Assist?")


@app.route('/login_req', methods=['GET', 'POST'])
def loginReq():
    user = request.form.get('username')
    password = request.form.get('password')

    #Convert to JSON
    dataStr = f'{{\"action\": \"log\", \"username\": \"{user}\", \"password\": \"{password}\"}}'
    dataClient.send(dataStr.encode('utf-8'))
    #Wait For Response on Login Request
    data = json.loads(dataClient.recv(4096).decode())
    #Error Handling
    if data.get("err") is not None:
        print(data["err"])
    else:
        global id
        id = data["id"]
        global stat
        global usern

        usern = user
        match (data["status"]):
            case ('member'): 
                stat = 1
            case ('leader'):
                stat = 2
            case _:
                stat = 0
    return render_template('index.html', panelUp='block', id=id, stat=stat, myHello=f"Hello {usern}! How Can I Assist?")

@app.route('/sign_req', methods=['GET', 'POST'])
def signReq():
    p1, p2 = request.form.get('password'), request.form.get('conf')
    global con

    if p1 != p2:
        #Confirmation Missed, Give Warning
        print("bs!")
        con = False
    else:
        if not con:
            con = True
        user = request.form.get('username')
        passw = request.form.get('password')
        dataStr = f'{{\"action\": \"sign\", \"username\": \"{user}\", \"password\": \"{passw}\"}}'
        dataClient.send(dataStr.encode('utf-8'))
        data = json.loads(dataClient.recv(4096).decode())
        if data.get("err") is not None:
            print(data["err"])
        else:
            global id
            id = data["id"]
            global stat
            match (data["status"]):
                case ('member'): 
                    stat = 1
                case ('leader'):
                    stat = 2
                case _:
                    stat = 0
            global usern
            usern = user
            
    return render_template('index.html', panelUp='Block', con=con, id=id, stat=stat, myHello=f"Hello {usern}! How Can I Assist?")

@app.route('/approve')
def approve_page():
    entry_id = request.args.get('entry_id')

    return f"""
    <h1>Approve Volunteer Hours</h1>
    <p>Entry ID: {entry_id}</p>

    <form method="POST" action="/approve_submit">
        <input type="hidden" name="entry_id" value="{entry_id}">
        <button name="decision" value="Y">Approve</button>
        <button name="decision" value="N">Reject</button>
    </form>
    """

@app.route('/approve_submit', methods=['POST'])
def approve_submit():
    entry_id = request.form.get('entry_id')
    decision = request.form.get('decision')

    dataStr = json.dumps({
        "action": "update",
        "id": int(entry_id),
        "ver": decision,
        "status": "approved" if decision == "Y" else "rejected"
    })

    dataClient.send(dataStr.encode())
    data = json.loads(dataClient.recv(4096).decode())

    return f"<h2>Submission {decision}</h2>"


if __name__ == "__main__":
    #Microservice TCP Socket Creation
    dataClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #Attempt Connection to Both Services (As of Right Now only port 5001)
    dataClient.connect(("db_service", 5001))
    Timer(1, openDash).start()
    app.run(host="0.0.0.0", port=5000)