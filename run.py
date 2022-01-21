import os
import platform

if platform.system() == "Linux":
    os.system("venv/bin/python main.pyw")
else:
    os.system("venv\Scripts\python.exe main.pyw")
