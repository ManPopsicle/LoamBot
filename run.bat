# Check for Python dependencies
pip3 install -r requirements.txt

# Launches VLC
START vlc --extraintf telnet --telnet-password pass --telnet-host 127.0.0.1 --telnet-port 5000

# Run Loambot
python Loambot.py