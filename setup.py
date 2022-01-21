import os
import time

try:
    print("[setup] Install...")
    os.system("python -m venv venv")
    os.system("venv\Scripts\pip install -r requirements.txt")
    print("[setup] Complete!")
    
except ValueError as error:
    print("[setup] "+error)


    











    






