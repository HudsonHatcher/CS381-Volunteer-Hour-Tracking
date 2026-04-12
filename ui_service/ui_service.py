#Import Dependencies
from flask import Flask, render_template, request
from threading import Timer
import webbrowser
import socket
import os

#Make Template directory for flask processing
try:
    os.mkdir('Templates')
except FileExistsError:
    pass

#Preset HTML Documents
dashboard = """
<!DOCTYPE html>
<html>
<style>div {
padding-top: 60px;
padding-left: 25px;
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
display: none;
margin-right: 25vh;
margin-left: 25vh;
border: 5px solid black;
border-radius: 15px;
justify-content: center;
align-items: center;
place-items: center;
background-color: lightpink;
height: 50vh;
width: 50vw;
margin-left: 24vw;
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
background-color: lightpink;
}
.wall {
display: none;
background: rgba(256, 256, 256, 0.5);
position: absolute;
top:0;
left:0;
height: 99vh;
width: 99vw;
}
</style>
<head><title>Hour Submission</title></head>
<body>
    <button type="button" style="width: 50px; height: 50px;" onclick="openLog()">Login Screen</button>
    <div>
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
</body>
<div class="wall" id="login_wall"></div>
<div class="login" id="login_panel">
    <button type="button" onclick="closeLog()" class="xBut">X</button>
    <h1 style="text-size:24px;">Login</h1>
    <form method='POST' action='login_req'>
        <p style="padding-top: 5vh;">
        <label style="text-size: 18px;">Username:</label><br>
        <input type="text" id="username" name="username" style="border: black; height: 25px; width: 50vh; border-radius: 15px;" placeholder=" username"></input>
        </p>
        <label style="text-size: 18px; padding-top: 5vh;">Password:</label><br>
        <input type="password" id="password" name="password" style="border: black; height: 25px; width: 50vh; border-radius: 15px;" placeholder=" password"></input><br>
        <p style="padding-top: 1vh;">
        <button type="submit" style="top-margin: 15px;">Login</button></p>
    </form>
</div>
</head>
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
</script>
</html>
"""

#Write Presets To Templates Directory
with open("Templates/index.html", "w") as file:
    file.write(dashboard)

#Setup Flask For Request Handling
app = Flask(__name__)

#Microservice TCP Socket Creation
dataClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Attempt Connection to Both Services (As of Right Now only port 8001)
dataClient.connect(("127.0.0.1", 8001))

#Flask Routing and Request Management
@app.route('/')
def homepage():
    return render_template('index.html')
@app.route('/submit_hour')
def submission():
    val = request.args['hourSub']
    #Verify That Request is A Number
    digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    for c in list(val):
        if c not in digits:
            return render_template('index.html', myErr='Please Enter a Number')
    #Clear Leading Zeros
    val = val.lstrip('0')
    
    dataStr = f"{{hours: {val}, userid: PlaceHolder}}"
    #Pass Integer Hour Submission to Database Handler
    dataClient.send(dataStr.encode('utf-8'))
    return render_template('index.html')

@app.route('/login_req', methods=['GET', 'POST'])
def loginReq():
    user = request.form.get('username')
    password = request.form.get('password')

    #Convert to JSON
    dataStr = f'{{username: {user}, password: {password}}}'
    dataClient.send(dataStr.encode('utf-8'))
    #Wait For Response on Login Request
    #data = recv(1024)
    return render_template('index.html')

#Open Browser
def openDash():
    webbrowser.open_new('http://127.0.0.1:5000')

#Run Flask
if __name__ == '__main__':
    Timer(1, openDash).start()
    app.run(port=5000)