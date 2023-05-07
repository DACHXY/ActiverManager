from typing import Optional, List
import subprocess
import psutil
from helper.string_parser import generate_uuid

class Backend:
    def __init__(self, id: int, cwd: str, run_server_cmd: str, update_cmd: str):
        self.id: int = id
        self.cwd: str = cwd
        self.cmd: list[str] = run_server_cmd.strip().split(" ")
        self.update_raw_cmd: list[str] = update_cmd.strip().split(" ")
        self.update_cmd: list[str] = update_cmd.strip().split(" ")
        self.process: Optional[subprocess.Popen] = None
        self.update_process: Optional[subprocess.Popen] = None
        self.status: str = "stop"
        self.process_pid: int = None

    def run(self) -> Optional[subprocess.Popen]:
        if not self.is_alive() and not self.is_updating():
            self.process = subprocess.Popen(self.cmd, cwd=self.cwd, shell=True)
        return self.process

    def stop(self) -> bool:
        if not self.is_alive():
            return False
        parent_pid = self.process.pid
        children = psutil.Process(self.process.pid).children(recursive=True)
        pids = [child.pid for child in children] + [parent_pid]
        # 終止整個進程樹
        for pid in pids:
            psutil.Process(pid).kill()
        self.process.wait(timeout=5)  # 等待子程序完全結束

        return_code = self.process.poll()
        if return_code is None:
            print("無法終止子程序, id:", self.id)
            return False
        elif return_code < 0:
            print("子程序被信號終止, id:", self.id)
        else:
            print("子程序已經結束, id:", self.id, "退出狀態碼:", return_code)

        self.process = None
        return True

    def is_alive(self) -> bool:
        try:
            status = psutil.Process(self.process.pid).status()
            if status == psutil.STATUS_RUNNING:
                return True
            elif status == psutil.STATUS_TERMINATED:
                return False
        except psutil.NoSuchProcess:
            return False
        except:
            return False

    def update(self):
        print("UPDATE STATUS:", self.is_updating())
        if not self.is_updating():
            if self.is_alive():
                self.stop()
            newuuid = generate_uuid()
            self.update_cmd = [newuuid if item == r'%%UUID%%' else item for item in self.update_raw_cmd]
            self.update_process = subprocess.Popen(self.update_cmd, shell=True)
        return self.update_process

    def is_updating(self) -> bool:
        try:
            status = psutil.Process(self.update_process.pid).status()
            if status == psutil.STATUS_RUNNING:
                return True
            elif status == psutil.STATUS_TERMINATED:
                return False
        except psutil.NoSuchProcess:
            return False
        except:
            return False

def create_backend_subclass(idx: int) -> type:
    return type(f"Backend{idx}", (Backend,), {})

# 建立所有的 Backend 實體
def create_backends(
    num_backends: int, backend_path: str, run_server_cmd: str, update_cmd: str
) -> List[Backend]:
    backend_class_list = [create_backend_subclass(i) for i in range(num_backends)]
    backends = [
        backend_class(backend_path=backend_path, run_server_cmd=run_server_cmd, update_cmd=update_cmd)()
        for backend_class in backend_class_list
    ]
    return backends
