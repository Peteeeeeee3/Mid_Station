from flask import Flask

app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    return "<h1>Mid_Station</h1>"

@app.route("/login")
def login():
    return "<h1>Login</h1>"