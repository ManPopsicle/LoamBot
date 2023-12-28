@REM Check for Python dependencies
pip3 install -r requirements.txt

@REM Launches VLC
@FOR /f "tokens=2*" %%i in ('Reg Query "HKEY_LOCAL_MACHINE\SOFTWARE\VideoLAN\VLC" /ve 2^>Nul') do Set "ExePath=%%j"
START "" "%ExePath%" --extraintf telnet --telnet-password pass --telnet-host 127.0.0.1 --telnet-port 5000

@REM # Run Loambot
python Loambot.py