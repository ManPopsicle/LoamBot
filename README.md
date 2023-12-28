# LoamBot
Discord bot for Sandy Loam's Discord server. Mostly here to make streaming cartoons easier.


# Features

This bot establishes a connection to your VLC interface, allowing you to control the stream bot through Discord commands.

- !play videos on VLC by accessing a MongoDB to dynamically seek and build a playlist of shows.
- Don't like what's on? Go to the !next episode! Don't like the show at all? !changechannel to another show!
- !shuffle on to get some variety. !shuffle off to keep it in season order.
- For more details, use !help


# Setup

The bot works by utilizing two Discord accounts: one regular user account (referred to as the stream bot henceforth), and one Discord bot account(referred to as Python bot henceforth). The stream bot acts solely to stream an instance of VLC Player in a voice chat of Discord, as Discord's API does not allow bots to stream. The Python bot is what this codebase runs and allows users to command the VLC Player.

This bot is meant to run on Windows.

The setup depends on having some other programs installed. You will need to grab the following:

1. Python - If you haven't already, download and install Python on your computer (https://www.python.org/downloads/). At minimum, please install Python 3.10. 
2. VLC Player - If you haven't already, download and install VLC Player on your computer (https://www.videolan.org/vlc/)
3. Microsoft C++ Build Tools - If you haven't already, you may need to download and install Microsoft C++ Build Tools to properly install the Python dependencies needed (https://visualstudio.microsoft.com/visual-cpp-build-tools/). This will involve downloading a large installer. Be sure to just grab the Desktop development tools to avoid having any more bloat than you need.

1. Clone the Loambot repo with ``git clone https://github.com/ManPopsicle/LoamBot.git`` or download the zip from Github.
2. Set up a Python bot on Discord (HOW TO MAKE A DISCORD BOT: https://discordpy.readthedocs.io/en/stable/discord.html). The bot will need read/write text channel permissions, including links, attachments and emojis, and message management. 
3. Set up your stream bot. Join the server and voice channel of your choice.
4. Navigate to LoamBot directory
5. Rename the ``config.yaml.example`` file to ``config.yaml`` and edit the fields (using a text editor of your choice) as necessary (Remember to turn on Developer mode in Discord to get your UserID for the config!)
6. Create a shortcut to VLC player on your desktop. Rename it ``vlc``.
6. Run the Python bot with ``run.bat``. A VLC GUI interface should pop up and Loambot should go online, and ready to control.
7. With your stream bot, begin streaming the opened VLC GUI instance.

You should now be able to run !play <show_name> to play a playlist. Make sure in the config.yaml file, under Libraries->Shows, the listed show names matches the file name of your VLC playlists (without the extension name). Also make sure that you keep all of your VLC playlist files in one location.



Questions? Comments? Send a message to SandyLoamAtSea on Discord. She's sure to answer you satisfactorily. 
