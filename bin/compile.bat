pip install -r requirements.txt
nuitka main.pyw -o Wallpaper.exe  --onefile --standalone --remove-output --windows-disable-console --windows-icon-from-ico=ico.ico --enable-plugin=pyqt5,numpy
