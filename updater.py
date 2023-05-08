import subprocess
import psutil
import sys
import os
import time

args = sys.argv

if len(args) > 1:
    pid = int(args[1])
else:
    # No arguments were passed
    pid = 0

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

def kill_by_pid(pid):
    os.system(f"taskkill /f /pid {pid}")

update_process = subprocess.Popen(["git", "pull"], shell=True)

if not pid == 0:
    kill_by_pid(pid)

while is_updating(update_process.pid):
    print("Updating...")
    time.sleep(2)
    
print("Update Done")

print("pip install...")
os.system("pip install -r requirements.txt")

print("Restart main Program...")
os.system("python main.py")