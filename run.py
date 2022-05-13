import os
import platform

if platform.system() == "Linux":
    os.system("venv/bin/python bin/main.pyw")
else:
    os.system("start venv\Scripts\pythonw.exe bin\main.pyw")
