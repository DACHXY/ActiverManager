import subprocess
import psutil
import time

def is_updating(pid) -> bool:
    try:
        status = psutil.Process(pid).status()
        if status == psutil.STATUS_RUNNING:
            return True
        elif status == psutil.STATUS_TERMINATED:
            return False
    except psutil.NoSuchProcess:
        return False
    except:
        return False

print("updater")

open("TEMP.txt", "w").close()

update_process = subprocess.Popen(["git", "pull"], shell=True)

while is_updating(update_process.pid):
    print("Updating...")
    time.sleep(2)

process = subprocess.Popen([ "../Scripts/activate.bat", "&&" ,"python", "main.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)