# LoamBot
Discord bot for Sandy Loam's Discord server. Mostly here to make streaming cartoons easier.


# Features

This bot establishes a connection to your VLC interface, allowing you to control the stream bot through Discord commands.

- !play your VLC playlists by listing them in your config.yaml
- Don't like what's on? Go to the !next episode! Don't like the show at all? !changechannel to another show!
- !shuffle on to get some variety. !shuffle off to keep it in season order.
- For more details, use !help


# Setup

You will need to set up both a Discord Bot (see above, referred to as Python bot henceforth), as well as an actual alternate Discord account (referred to as the stream bot henceforth).

1. Make a Python bot (HOW TO MAKE A DISCORD BOT: https://discordpy.readthedocs.io/en/stable/discord.html). Bot will need read/write text channel permissions, including links, attachments and emojis, and message management. 
2. Set up your stream bot. Join the server and voice channel of your choice.
3. Clone the Loambot repo with ``git clone https://github.com/ManPopsicle/LoamBot.git`` or download the zip from Github.
4. Navigate to LoamBot directory
5. Install dependencies with ``pip3 install -r requirements.txt``
6. Rename the ``config.yaml.example`` file to ``config.yaml`` and edit as necessary (Remember to turn on Developer mode in Discord to get your UserID for the config!)
7. Run the ``vlc_cli.bat`` file. A VLC GUI instance should open.
8. With your stream bot, begin streaming the opened VLC GUI instance.
8. Run the Python bot with ``python3 Loambot.py`` or ``python Loambot.py`` or ``py Loambot.py``. Loambot should go online. and ready to control.

You should now be able to run !play <show_name> to play a playlist. Make sure in the config.yaml file, under Libraries->Shows, the listed show names matches the file name of your VLC playlists. Also make sure that you keep all of your VLC playlist files in one location.


# TO DO

- Path to the show playlists is currently hardcoded. Make it more flexible by changing it to whatever the admin wants
- Support for movie nights
- A "historically accurate time" playlist that will play shows of the same time period



Questions? Comments? Send a message to SandyLoamAtSea on Discord. She's sure to answer you satisfactorily. 