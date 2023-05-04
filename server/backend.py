from typing import Optional, Union, List
import subprocess

class Backend:
    def __init__(self, id: int, cwd: str, run_server_cmd: str):
        self.id: int = id
        self.cwd: str = cwd
        self.cmd: list[str] = run_server_cmd.split(" ")
        self.process: Optional[subprocess.Popen] = None

    def run(self) -> Optional[subprocess.Popen]:
        if not self.is_alive():
            self.process = subprocess.Popen(self.cmd, cwd=self.cwd)
        return self.process

    def stop(self) -> bool:
        if not self.is_alive():
            return False
        self.process.kill()
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
        if self.process is None:
            return False
        elif self.process.poll() is not None:
            self.process = None
            return False
        else:
            return True

def create_backend_subclass(idx: int) -> type:
    return type(f"Backend{idx}", (Backend,), {})


# 建立所有的 Backend 實體
def create_backends(
    num_backends: int, backend_path: str, run_server_cmd: str
) -> List[Backend]:
    backend_class_list = [create_backend_subclass(i) for i in range(num_backends)]
    backends = [
        backend_class(backend_path=backend_path, run_server_cmd=run_server_cmd)()
        for backend_class in backend_class_list
    ]
    return backends
