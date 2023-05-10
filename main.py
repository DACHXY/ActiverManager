from typing import Optional
from flask import Flask, request, render_template, jsonify
from server.backend import Backend
from models.db_model import db, Server
import os
import subprocess
from werkzeug.serving import make_server
import threading


## Config
HOME_PATH = "home.html"
IP = "0.0.0.0"
PORT = 5050

## Initial Variable
BACKENDS: list[Backend] = []


def add_new_backend(
    server_id: int, backend_path: str, run_server_cmd: str, update_cmd: str
):
    new_backend = Backend(
        id=server_id,
        cwd=backend_path,
        run_server_cmd=run_server_cmd,
        update_cmd=update_cmd,
    )
    BACKENDS.append(new_backend)


def delete_backend_by_id(id: int):
    for i, item in enumerate(BACKENDS):
        if item.id == id:
            del BACKENDS[i]
            break


def create_backend_instances(servers: list[Server]) -> list[Backend]:
    backends = []
    for server in servers:
        backend = Backend(
            id=server.id,
            cwd=server.cwd,
            run_server_cmd=server.exec_cmd,
            update_cmd=server.update_cmd,
        )
        backends.append(backend)
    return backends


def find_backend_by_id(lst: list[Backend], target_id) -> Backend:
    if (item := next((item for item in lst if item.id == target_id), None)) is not None:
        return item
    else:
        raise ValueError(f"Item with id {target_id} not found in list")


app: Flask = Flask(__name__, template_folder="templates")
app.debug = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    app.root_path, "data", "activerManager.db"
)
db.init_app(app)

with app.app_context():
    # 創建所有資料表
    db.create_all()
    servers: list[Server] = db.session.execute(db.select(Server)).scalars()
    # 初始化所有資料庫
    BACKENDS = create_backend_instances(servers)


# App routes defined here
@app.route("/update-program", methods=["GET"])
def update_main():
    print("UPDATE")
    pid = os.getpid()
    os.system(f"python updater.py {pid}")
    return jsonify(status_code=201, msg="Server shutting down..."), 201


@app.route("/", methods=["GET"])
def index():
    return render_template(HOME_PATH)


@app.route("/<int:id>", methods=["DELETE"])
def delete_server(id: int):
    with app.app_context():
        server: Server = Server.query.get(id)
        db.session.delete(server)
        db.session.commit()
    delete_backend_by_id(id=id)
    return jsonify(status_code=200, msg=f"Id: {id} 已刪除"), 200


@app.route("/<int:id>", methods=["POST"])
def update_server_info(id: int):
    req_data = request.get_json()
    servername: str = req_data["servername"]
    exec_cmd: str = req_data["exec_cmd"]
    cwd: str = req_data["cwd"]
    update_cmd: str = req_data["update_cmd"]
    with app.app_context():
        server: Server = Server.query.get(id)
        server.servername = servername
        server.exec_cmd = exec_cmd
        server.cwd = cwd
        server.update_cmd = update_cmd
        db.session.commit()
        delete_backend_by_id(id)
        add_new_backend(
            server_id=server.id,
            backend_path=server.cwd,
            run_server_cmd=server.exec_cmd,
            update_cmd=update_cmd,
        )
    return jsonify(status_code=200, msg="更新成功"), 200


@app.route("/run/<int:id>", methods=["GET"])
def start_server(id: int):
    status: Optional[subprocess.Popen] = find_backend_by_id(BACKENDS, id).run()
    if status is None:
        return jsonify(status_code=200, msg="後端已經在運行"), 200
    return jsonify(status_code=200, msg="後端開始運行"), 200


@app.route("/stop/<int:id>", methods=["GET"])
def stop_server(id: int):
    status: bool = find_backend_by_id(BACKENDS, id).stop()
    if status:
        return jsonify(status_code=200, msg="後端伺服器已停止運作"), 200
    return jsonify(status_code=200, msg="後端伺服器沒有運作或發生錯誤"), 200


@app.route("/update/<int:id>", methods=["GET"])
def update_server_version(id: int):
    status = find_backend_by_id(BACKENDS, id).update()
    if status is None:
        print("更新失敗 id:", id)
        return jsonify(status_code=500, msg="更新失敗"), 500
    return jsonify(status_code=200, msg="更新完成"), 200


@app.route("/all", methods=["GET"])
def get_all_server():
    servers: list[Server] = db.session.execute(db.select(Server)).scalars()
    servers_dict_list: list[Backend] = []
    for server in servers:
        backend = find_backend_by_id(BACKENDS, server.id)
        servers_dict_list.append(
            server.to_dict(
                is_alive=backend.is_alive(), is_updating=backend.is_updating()
            )
        )
    return jsonify(status_code=200, servers=servers_dict_list), 200


@app.route("/add", methods=["POST"])
def add_new_server():
    req_data = request.get_json()
    servername: str = req_data["servername"]
    exec_cmd: str = req_data["exec_cmd"]
    cwd: str = req_data["cwd"]
    update_cmd: str = req_data["update_cmd"]

    # 加入資料庫
    with app.app_context():
        new_server: Server = Server(
            servername=servername, exec_cmd=exec_cmd, cwd=cwd, update_cmd=update_cmd
        )
        db.session.add(new_server)
        db.session.commit()

        # 加入 backend 運行實體
        add_new_backend(
            server_id=new_server.id,
            backend_path=new_server.cwd,
            run_server_cmd=new_server.exec_cmd,
            update_cmd=new_server.update_cmd,
        )

    return jsonify(status_code=200, msg="新增成功"), 200


if __name__ == "__main__":
    print("server started, listening:", f"{IP}:{PORT}")
    app.run(host=IP, port=PORT)
