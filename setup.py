import os
import time
import platform

print("[setup] Install...")
if platform.system() == "Linux":
    os.system("python3 -m venv venv")
    os.system("venv/bin/pip install -r bin/requirements.txt")
else:
    os.system("python -m venv venv")
    os.system("venv\Scripts\pip install -r bin/requirements.txt")
print("[setup] Complete!")
input("Press enter to exit...")



    











    






