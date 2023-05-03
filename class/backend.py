from typing import Optional, Union
import subprocess

class Backend():
    def __init__(self, backend_path : str, run_server_cmd : str):
        self.path : str = backend_path
        self.run_server_cmd : list[str] = run_server_cmd.split(" ")
        self.server_process : subprocess.Popen = None

    def run(self) -> Optional[subprocess.Popen]:
        try:
            self.server_process = subprocess.Popen(self.run_server_cmd, cwd=self.path)
            return self.server_process
        except:
            return None
        
    def stop(self) -> True:
        self.server_process.stop()

    def is_server_alive(self) -> bool:
        return self.server_process is None or self.server_process.poll() is not None