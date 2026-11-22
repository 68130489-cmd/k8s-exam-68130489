from flask import Flask, render_template, request, redirect, jsonify
from pathlib import Path
import os
import json
import tempfile

app = Flask(__name__)

DATA_DIR = Path("/data")
DATA_FILE = DATA_DIR / "research.txt"
DEFAULT_FILE = Path("/app/research.txt")
PORTAL_FILE = DATA_DIR / "portal.json"

DEFAULT_PORTAL = {
    "student_id": "68130489",
    "name": "อรรถพล พวงทิพย์วรรณ",
    "cluster": "3 Nodes",
    "control_plane": "1 Node",
    "worker_nodes": "2 Nodes"
}

def atomic_write(path, content):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        dir=str(DATA_DIR),
        encoding="utf-8",
        delete=False
    ) as f:
        f.write(content)
        temp_path = f.name
    os.replace(temp_path, path)

def read_research():
    if DATA_FILE.exists():
        return DATA_FILE.read_text(encoding="utf-8")
    return DEFAULT_FILE.read_text(encoding="utf-8")

def read_portal():
    if PORTAL_FILE.exists():
        data = json.loads(PORTAL_FILE.read_text(encoding="utf-8"))
        return {**DEFAULT_PORTAL, **data}
    return DEFAULT_PORTAL.copy()

@app.route("/")
def index():
    return render_template("admin.html")

@app.route("/research")
def research():
    return render_template(
        "research.html",
        content=read_research()
    )

@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        content = request.form.get("content", "")
        atomic_write(DATA_FILE, content)
        return redirect("/edit?saved=1")

    return render_template(
        "edit.html",
        content=read_research(),
        saved=request.args.get("saved")
    )

@app.route("/edit-portal", methods=["GET", "POST"])
def edit_portal():
    if request.method == "POST":
        data = {
            key: request.form.get(key, "").strip()
            for key in DEFAULT_PORTAL
        }

        if not all(data.values()):
            return "กรุณากรอกข้อมูลให้ครบ", 400

        atomic_write(
            PORTAL_FILE,
            json.dumps(data, ensure_ascii=False, indent=2)
        )
        return redirect("/edit-portal?saved=1")

    return render_template(
        "edit_portal.html",
        portal=read_portal(),
        saved=request.args.get("saved")
    )

@app.route("/portal-data")
def portal_data():
    return jsonify(read_portal())
