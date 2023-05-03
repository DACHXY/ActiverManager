from typing import Optional, Union
import subprocess

class Backend():
    def __init__(self, backend_path : str, run_server_cmd : str):
        self.path : str = backend_path
        self.run_server_cmd : list[str] = run_server_cmd.split(" ")
        self.server_process : subprocess.Popen = None

    def run(self) -> Optional[subprocess.Popen]:
        if not self.is_server_alive():
            self.server_process = subprocess.Popen(self.run_server_cmd, cwd=self.path)
        return self.server_process
        
    def stop(self) -> bool:
        if not self.is_server_alive():
            return False
        self.server_process.kill()
        return True

    def is_server_alive(self) -> bool:
        return not self.server_process is None or self.server_process.poll() is not None
    
    