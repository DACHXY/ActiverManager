from flask import Flask
import subprocess

app = Flask(__name__)

server_process = None
BACKEND_PATH = ""


@app.route('/start')
def start_server():
    global server_process
    if server_process is None or server_process.poll() is not None:
        server_process = subprocess.Popen(['dotnet', 'run'], cwd=BACKEND_PATH)
        return 'Server started'
    else:
        return 'Server is already running'

@app.route('/stop')
def stop_server():
    global server_process
    if server_process is not None and server_process.poll() is None:
        server_process.kill()
        server_process = None
        return 'Server stopped'
    else:
        return 'Server is not running'

if __name__ == "__main__":
    app.run()