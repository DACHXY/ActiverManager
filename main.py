from typing import Optional, Union
from flask import Flask, render_template, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from server.backend import Backend
import subprocess

app : Flask = Flask(__name__, template_folder="templates")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db : SQLAlchemy = SQLAlchemy(app)

## Config
BACKEND_PATH = r"C:\\Users\danny\Documents\DN\Projects\Activer\backend"
BACKEDN_RUN_CMD = "dotnet run"

## HTML Config
HOME_PATH = "home.html"

## 初始化 backend server 
backend_server : Backend = Backend(
    backend_path=BACKEND_PATH, 
    run_server_cmd=BACKEDN_RUN_CMD
    )

@app.route("/", methods=["GET"])
def index():
    return render_template(HOME_PATH), 200

@app.route("/start", methods=["GET"])
def start_backend():
    status : Optional[subprocess.Popen] = backend_server.run()
    if status is None:
        return jsonify(status_code=200, msg="後端已經在運行"), 200
    return jsonify(status_code=200, msg="後端開始運行"), 200

@app.route("/status", methods=["GET"])
def get_backend_status():
    status : str = "running" if backend_server.is_server_alive() else "stopped"
    return jsonify(status_code=200, status=status), 200

@app.route("/stop", methods=["GET"])
def stop_backend():
    status : bool = backend_server.stop()
    if status:
        return jsonify(status_code=200, msg="後端伺服器已停止運作"), 200
    return jsonify(status_code=200, msg="後端伺服器沒有運作或發生錯誤"), 200

@app.route("/all")
def get_all_server():
    return None

if __name__ == "__main__":
    app.run()