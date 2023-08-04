from flask import Flask, render_template, request, redirect, session, jsonify
from zenora import APIClient
from bs4 import BeautifulSoup
import json
import requests


#設定
url=""
id="1120561509400072222"
bot_token=""
client_secret=""
admins=[851062442330816522]
#


app = Flask(__name__)
client = APIClient(token=bot_token,client_secret=client_secret)
app.config["SECRET_KEY"] = "mysecret"


@app.route("/", methods=["GET"])
def home():
    access_token = session.get("access_token")

    if not access_token:
        return redirect(f"/login")
    
    bearer_client = APIClient(access_token, bearer=True)
    current_user = bearer_client.users.get_current_user()

    if not current_user.id in admins:
        return render_template("login.html")
    
    with open("urls.json","r",encoding="utf-8")as f:
        data=json.load(f)
    info={}
    times=0
    urls=0
    for i in data:
        if data[i]!=None:
            times+=data[i]["looks"]
            urls+=1
    
    info["times"]=times
    info["urls"]=urls
    info["users"]=len(admins)
    return render_template("index.html",user=current_user,data=data,info=info)

@app.route("/add", methods=["GET","POST"])
def add():
    access_token = session.get("access_token")

    if not access_token:
        return redirect(f"/login")
    
    bearer_client = APIClient(access_token, bearer=True)
    current_user = bearer_client.users.get_current_user()

    if not current_user.id in admins:
        return redirect(f"/")
    
    with open("urls.json","r",encoding="utf-8")as f:
        data=json.load(f)
    if request.method == "POST":
        data[request.form["code"]]={}
        data[request.form["code"]]["target"]=request.form["url"]
        data[request.form["code"]]["looks"]=0

        title=request.form["name"]
        if title=="":
            try:
                url = request.form["url"]
                html = requests.get(url,timeout=3)
                html.encoding = "utf-8"
                sp = BeautifulSoup(html.text, 'html.parser')
                if len(sp.title.text)>10:
                    data[request.form["code"]]["title"]=sp.title.text[:15]
                else:
                    data[request.form["code"]]["title"]=sp.title.text
            except:
                data[request.form["code"]]["title"]="未知"
        else:
            data[request.form["code"]]["title"]=request.form["name"]
        with open("urls.json","w",encoding="utf-8")as f:
            json.dump(data,f)
        return redirect(f"/")
    
    info={}
    times=0
    urls=0
    for i in data:
        if data[i]!=None:
            times+=data[i]["looks"]
            urls+=1
    
    info["times"]=times
    info["urls"]=urls
    info["users"]=len(admins)
    return render_template("add.html",user=current_user,data=data,info=info)

@app.route("/del/<code>", methods=["GET"])
def dle(code):
    access_token = session.get("access_token")

    if not access_token:
        return redirect(f"/login")
    
    bearer_client = APIClient(access_token, bearer=True)
    current_user = bearer_client.users.get_current_user()

    if not current_user.id in admins:
        return redirect(f"/")
    with open("urls.json","r",encoding="utf-8")as f:
        data=json.load(f)
    try:
        if data[code] == None:
            return redirect("/")
        data[code]=None
        with open("urls.json","w",encoding="utf-8")as f:
            json.dump(data,f)
    except:
        pass
    return redirect(f"/")

@app.route("/<code>", methods=["GET"])
def u(code):
    with open("urls.json","r",encoding="utf-8")as f:
        data=json.load(f)
    try:
        if data[code] == None:
            return redirect("/")
        data[code]["looks"]+=1
        with open("urls.json","w",encoding="utf-8")as f:
            json.dump(data,f)
        return redirect(data[code]["target"])
    except:
        return redirect(f"/")

@app.route("/login")
def login():
    return redirect(f"https://discord.com/api/oauth2/authorize?client_id={id}&redirect_uri={url}oauth/callback&response_type=code&scope=identify%20guilds%20email")


@app.route("/logout")
def logout():
    session.pop("access_token")
    return redirect("/")


@app.route("/oauth/callback")
def oauth_callback():
    code = request.args["code"]
    access_token = client.oauth.get_access_token(
        code, redirect_uri=f"{url}oauth/callback"
    ).access_token
    session["access_token"] = access_token
    return redirect("/")

app.run(debug=True)