import os
import time
import platform


if platform.system() == "Linux":
    print("[setup] Install...")
    os.system("python -m venv venv")
    os.system("venv/bin/pip install -r requirements.txt")
    print("[setup] Complete!")

else:
    print("[setup] Install...")
    os.system("python -m venv venv")
    os.system("venv\Scripts\pip install -r requirements.txt")
    print("[setup] Complete!")
    



    











    






