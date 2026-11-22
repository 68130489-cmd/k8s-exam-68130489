from flask import Flask, render_template

app = Flask(__name__)

@app.route("/api-489")
@app.route("/api-489/")
@app.route("/api")
@app.route("/api/")
def index():
    return render_template(
        "index.html",
        message="Welcome to API Service"
    )

@app.route("/api/<path:message>")
def show_message(message):
    return render_template(
        "index.html",
        message=message
    )

