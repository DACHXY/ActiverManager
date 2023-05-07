import subprocess
print("updater")

open("TEMP.txt", "w").close()

subprocess.Popen(["git", "pull"])