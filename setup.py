import os
import time
import platform

print("[setup] Install...")
os.system("python -m venv venv")
if platform.system() == "Linux":
    os.system("venv/bin/pip install -r bin/requirements.txt")
else:
    os.system("venv\Scripts\pip install -r bin/requirements.txt")
print("[setup] Complete!")
input("Press enter to exit...")



    











    






