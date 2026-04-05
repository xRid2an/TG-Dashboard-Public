# TG-Dashboard-Public
This is an alpha version of my development project, free to fork.

#!/bin/bash

pkg update && pkg upgrade -y
pkg install python -y
pkg install git -y
pkg install pip -y
git clone https://github.com/xRid2an/TG-Dashboard-Public
cd TG-Dashboard-Public
pip install -r requirements.txt
python app.py

Created and developed by xRid2an ©2026 All right reserved
