import os

import discord
from discord.ext import commands

import vlc
from televlc import televlc

from modules import config_parser
from modules.logs import *

# VLC class for controlling the player through Python
# class VLC:

#     def __init__(self):
#         self.Player = vlc.Instance('--loop')
#         self.listPlayer = self.Player.media_list_player_new()

#     def addPlaylist(self, playlist):
#         mediaList = self.Player.media_list_new()
#         path = r"D:\Shows\[Playlist]\\" + playlist + ".xspf"
#         mediaList.add_media(self.Player.media_new(path))
#         self.listPlayer.set_media_list(mediaList)

#     def play(self):
#         self.listPlayer.play()

#     def next(self):
#         self.listPlayer.next()

#     def pause(self):
#         self.listPlayer.pause()

#     def previous(self):
#         self.listPlayer.previous()

#     def stop(self):
#         self.listPlayer.stop()




#############################################################################################################################

# Parse config
config = config_parser.Config(app_name="Loambot", config_path="config.yaml")

# Start logger
logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.getLevelName(config.log_level))

# Instantiate Discord bot representation
bot = commands.Bot(command_prefix=config.discord.bot_prefix, intents=discord.Intents.all())

# Help command?
formatter = commands.HelpCommand(show_check_failure=False)

info("Starting application...")

PASSWORD = config.vlc.password
HOST = config.vlc.host
PORT = config.vlc.port

# Initialize the vlc object
vlc = televlc.VLC(PASSWORD, HOST, PORT)
print(vlc.connect_to_telnet_interface())

# on_ready event for setting up status after log in is successful
# TODO: Write a function to update activity when playlist changes
@bot.event
async def on_ready():
    info(f'\n\nLogged in as : {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming! | {config.discord.bot_prefix}'))
    info(f'Successfully logged in and booted...!\n')





######################################################################
# COMMANDS FOR PLAYING A PLAYLIST
# AVAILABLE PLAYLISTS:
# - Boondocks
# - Courage the Cowardly Dog
# - Ed, Edd n' Eddy
# - Fresh Prince of Bel-Air
# - Futurama
# - It's Always Sunny In Philadelphia
# - King of the Hill
# - Metalocalypse
# - Samurai Jack
# - Seinfeld
# - Spongebob Squarepants
#######################################################################
#Boondocks
@bot.command(aliases = ["boondocks", "Boondocks"], description = ": Plays The Boondocks seasons 1-4.")
async def playBoondocks(message):
    await message.channel.send("NOW PLAYING THE BOONDOCKS!")
    
#Courage
@bot.command(aliases = ["courage", "Courage", "couragethecowardlydog", "stupiddog"], description = ": Plays Courage the Cowardly Dog seasons 1-4.")
async def playCourage(message):
    await message.channel.send("NOW PLAYING COURAGE THE COWARDLY DOG!")
        
#Eds
@bot.command(aliases = ["ed", "eds", "ededdeddy"], description = ": Plays Ed, Edd n' Eddy seasons 1-6.")
async def playEds(message):
    await message.channel.send("NOW PLAYING ED, EDD N' EDDY!")

#Fresh Prince
@bot.command(aliases = ["will", "belair", "freshprince", "freshprinceofbelair"], description = ": Plays Fresh Prince of Bel-Air seasons 1-6.")
async def playFreshPrince(message):
    await message.channel.send("NOW PLAYING FRESH PRINCE OF BEL-AIR!")

#Futurama
@bot.command(aliases = ["futurama", "Futurama"], description = ": Plays Futurama seasons 1-7.")
async def playFuturama(message):
    await message.channel.send("NOW PLAYING FUTURAMA!")

#Always Sunny
@bot.command(aliases = ["alwayssunny", "philly"], description = ": Plays It's Always Sunny In Philadelphia seasons 1-13.")
async def playPhilly(message):
    await message.channel.send("NOW PLAYING IT'S ALWAYS SUNNY IN PHILADELPHIA!")

#Koth
@bot.command(aliases = ["kingofthehill", "koth"], description = ": Plays King of the Hill seasons 1-13.")
async def playKoth(message):
    await message.channel.send("NOW PLAYING KING OF THE HILL!")

#Metalocalypse
@bot.command(aliases = ["metalocalypse", "deathklok", "Metalocalypse", "Deathklok"], description = ": Plays Metalocalypse seasons 1-4.")
async def playMetalocalypse(message):
    await message.channel.send("NOW PLAYING METALOCALYPSE!")

#Samurai Jack
@bot.command(aliases = ["jack", "samuraijack"], description = ": Plays Samurai Jack seasons 1-5.")
async def playJack(message):
    await message.channel.send("NOW PLAYING SAMURAI JACK!")


#Seinfeld
@bot.command(aliases = ["seinfeld", "Seinfeld"], description = ": Plays Seinfeld seasons 1-9.")
async def playSeinfeld(message):
    await message.channel.send("NOW PLAYING Seinfeld!")

#Spongebob
@bot.command(aliases = ["spongebob", "Spongebob", "Spongebob Squarepants"], description = ": Plays Spongebob Squarepants seasons 1-10.")
async def playSpongebob(message):
    catEmoji = discord.utils.get(message.guild.emojis, name="threatencat")
    await message.channel.send("NOW PLAYING SPONGEBOB! " + str(catEmoji))




########################################################################################################################


# Begin running
if __name__ == '__main__':
    info("Connecting to Discord...")
    bot.run(config.discord.bot_token)
