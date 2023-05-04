from typing import Optional, Union
from flask import Flask, request, render_template, jsonify
from server.backend import Backend
from models.db_model import db, Server
import os
import subprocess


def create_backend_instances(servers: list[Server]) -> list[Backend]:
    backends = []
    for server in servers:
        backend = Backend(id=server.id, cwd=server.cwd, run_server_cmd=server.exec_cmd)
        backends.append(backend)
    return backends


def find_backend_by_id(lst: list[Backend], target_id) -> Backend:
    if (item := next((item for item in lst if item.id == target_id), None)) is not None:
        return item
    else:
        raise ValueError(f"Item with id {target_id} not found in list")


## Config
BACKEND_PATH = r"C:\\Users\danny\Documents\DN\Projects\Activer\backend"
BACKEDN_RUN_CMD = "dotnet run"

## HTML Config
HOME_PATH = "home.html"

app: Flask = Flask(__name__, template_folder="templates")
app.debug = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    app.root_path, "data", "activerManager.db"
)
db.init_app(app)

BACKENDS: list[Backend] = []

with app.app_context():
    # 創建所有資料表
    db.create_all()
    servers: list[Server] = Server.query.all()
    # 初始化所有資料庫
    BACKENDS = create_backend_instances(servers)


@app.route("/", methods=["GET"])
def index():
    servers: list[Server] = Server.query.all()
    servers_dict_list = [
        server.to_dict(is_alive=find_backend_by_id(BACKENDS, server.id).is_alive())
        for server in servers
    ]

    return render_template(HOME_PATH, servers=servers_dict_list)


# @app.route("/start", methods=["GET"])
# def start_backend():
#     status: Optional[subprocess.Popen] = backend_server.run()
#     if status is None:
#         return jsonify(status_code=200, msg="後端已經在運行"), 200
#     return jsonify(status_code=200, msg="後端開始運行"), 200


# @app.route("/status", methods=["GET"])
# def get_backend_status():
#     status: str = "running" if backend_server.is_server_alive() else "stopped"
#     return jsonify(status_code=200, status=status), 200


# @app.route("/stop", methods=["GET"])
# def stop_backend():
#     status: bool = backend_server.stop()
#     if status:
#         return jsonify(status_code=200, msg="後端伺服器已停止運作"), 200
#     return jsonify(status_code=200, msg="後端伺服器沒有運作或發生錯誤"), 200


@app.route("/all", methods=["GET"])
def get_all_server():
    servers = Server.query.all()
    servers_dict_list = [server.to_dict() for server in servers]
    return jsonify(status_code=200, servers=servers_dict_list), 200


@app.route("/add", methods=["POST"])
def add_new_server():
    req_data = request.get_json()
    servername: str = req_data["servername"]
    exec_cmd: str = req_data["exec_cmd"]
    cwd: str = req_data["cwd"]
    with app.app_context():
        new_server: Server = Server(servername=servername, exec_cmd=exec_cmd, cwd=cwd)
        db.session.add(new_server)
        db.session.commit()
    return jsonify(status_code=200)


if __name__ == "__main__":
    app.run()
