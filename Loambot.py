import os

import discord
from discord.ext import commands

import vlc
from python_telnet_vlc import VLCTelnet

from modules import config_parser
from modules.logs import *

from enum import Enum

class showPlaylistToTitle(Enum):
    boondocks = "The Boondocks"
    chowder = "Chowder"
    courage = "Courage the Cowardly Dog"
    eds = "Ed, Edd n Eddy"
    freshprince = "The Fresh Prince of Bel-Air"
    futurama = "Futurama"
    koth = "King of the Hill"
    metalocalypse = "Metalocalypse"
    jack = "Samurai Jack"
    seinfeld = "Seinfeld"
    spongebob = "Spongebob Squarepants"
    sunny = "It's Always Sunny In Philadelphia"
    zim = "Invader Zim"

# Returns a properly formatted version of a show name
def iterShowEnum(listItem):
    for member in showPlaylistToTitle:
        if listItem == member.name:
            return member.value
    
    return "Not found!"
#############################################################################################################################

# Parse config
config = config_parser.Config(app_name="Loambot", config_path="config.yaml")


# Start logger
logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.getLevelName(config.log_level))

# Initialize the vlc object
PASSWORD = config.vlc.password
HOST = config.vlc.host
PORT = config.vlc.port
vlc = VLCTelnet(HOST, PASSWORD, PORT)    

vlcIsShuffled = config.vlc.shuffle
shuffle = 'on' if vlcIsShuffled else 'off'
vlc.random(False, shuffle)

# Instantiate Discord bot representation
bot = commands.Bot(command_prefix=config.discord.bot_prefix, intents=discord.Intents.all(), help_command=None)

# Help command?
#formatter = commands.HelpCommand(show_check_failure=False)

info("Starting application...")



# on_ready event for setting up status after log in is successful
# TODO: Write a function to update activity when playlist changes
@bot.event
async def on_ready():
    info(f'\n\nLogged in as : {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Loambot set to kill.'))
    info(f'Successfully logged in and booted...!\n')



######################################################################
# COMMANDS FOR PLAYING A PLAYLIST
# AVAILABLE PLAYLISTS:
# - Boondocks
# - Chowder
# - Courage the Cowardly Dog
# - Ed, Edd n' Eddy
# - Fresh Prince of Bel-Air
# - Futurama
# - Invader Zim
# - It's Always Sunny In Philadelphia
# - King of the Hill
# - Metalocalypse
# - Samurai Jack
# - Seinfeld
# - Spongebob Squarepants
#######################################################################
# Help command 
@bot.command(aliases = ["help"], description = ": Chooses a playlist from list of shows based on user argument and plays it.")
async def commands(message):
    await message.channel.send("""```
        Available commands: 
        !play <show_name> : Choose a show to play
        !shuffle : Toggles the shuffle function. Next episode of the show will be randomized.
        !changechannel or !cc : Changes the channel! A different playlist begins playing
                               ```""")
  


# General play command for shows. Argument should be one of the names of the playlist
@bot.command(aliases = ["play"], description = ": Chooses a playlist from list of shows based on user argument and plays it.")
async def playShow(message, arg):
    # Look for user input in the library list
    if arg in config.libraries.shows_library:
        # Playlist found. Locate it in the file directory and play it
        vlc.clear()
        playlist = "D:\\Shows\\[Playlist]\\" + arg + ".xspf"
        vlc.add(playlist)
        vlc.play()
        # Announce it
        await message.channel.send("NOW PLAYING " + iterShowEnum(arg).upper())
        # Change bot's status to reflect new playlist
        await bot.change_presence(status=discord.Status.idle,
                                activity=discord.Game(name=f'Now streaming ' + iterShowEnum(arg)))
        
    # No playlist found; play the master playlist
    else:
        vlc.clear()
        playlist = "D:\\Shows\\[Playlist]\\all.xspf"
        vlc.add(playlist)
        vlc.play()
        # Announce it
        await message.channel.send("NOW PLAYING WHATEVER COMES TO MIND!")
        # Change bot's status to reflect new playlist
        await bot.change_presence(status=discord.Status.idle,
                                activity=discord.Game(name=f'Now streaming whatever!'))
        

# Shuffle command
@bot.command(aliases = ["shuffle"], description = ": Chooses a playlist from list of shows based on user argument and plays it.")
async def shufflePlaylist(message, arg = None):
    global vlcIsShuffled
    if arg == "on":
        vlc.random(True)
        catEmoji = discord.utils.get(message.guild.emojis, name="catrave")
        await message.channel.send(str(catEmoji) + " Shuffle is now on. " + str(catEmoji))
        vlcIsShuffled = True 
    elif arg == "off":
        vlc.random(False)
        catEmoji = discord.utils.get(message.guild.emojis, name="imdie")
        await message.channel.send(str(catEmoji) + " Shuffle is now off. " + str(catEmoji))
        vlcIsShuffled = False
    else:
        vlc.random()
        catEmoji = discord.utils.get(message.guild.emojis, name="doghittinit")
        vlcIsShuffled = not vlcIsShuffled
        await message.channel.send(str(catEmoji) + " Shuffle toggled to " + str(vlcIsShuffled) + ". " + str(catEmoji))




#Boondocks
@bot.command(aliases = ["boondocks", "Boondocks", "person"], description = ": Plays The Boondocks seasons 1-4.")
async def playBoondocks(message):
    await message.channel.send("NOW PLAYING THE BOONDOCKS!")
    
    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming The Boondocks!'))
    

#Chowder
@bot.command(aliases = ["chowder"], description = ": Plays Chowder seasons 1-3.")
async def playChowder(message):
    await message.channel.send("NOW PLAYING CHOWDER!")
    
    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming Chowder!'))
    

#Courage
@bot.command(aliases = ["courage", "Courage", "couragethecowardlydog", "stupiddog"], description = ": Plays Courage the Cowardly Dog seasons 1-4.")
async def playCourage(message):
    await message.channel.send("NOW PLAYING COURAGE THE COWARDLY DOG!")
    
    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming Courage the Cowardly Dog!'))
    

#Eds
@bot.command(aliases = ["ed", "eds", "ededdeddy", "canadians"], description = ": Plays Ed, Edd n' Eddy seasons 1-6.")
async def playEds(message):
    await message.channel.send("NOW PLAYING ED, EDD N' EDDY!")
    
    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming Ed, Edd n Eddy!'))


#Fresh Prince
@bot.command(aliases = ["will", "belair", "freshprince", "freshprinceofbelair"], description = ": Plays Fresh Prince of Bel-Air seasons 1-6.")
async def playFreshPrince(message):
    await message.channel.send("NOW PLAYING FRESH PRINCE OF BEL-AIR!")
    
    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming The Fresh Prince of Bel-Air!'))


#Futurama
@bot.command(aliases = ["futurama", "Futurama"], description = ": Plays Futurama seasons 1-7.")
async def playFuturama(message):
    await message.channel.send("NOW PLAYING FUTURAMA!")
    
    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming Futurama!'))


#Always Sunny
@bot.command(aliases = ["alwayssunny", "philly"], description = ": Plays It's Always Sunny In Philadelphia seasons 1-13.")
async def playPhilly(message):
    await message.channel.send("NOW PLAYING IT'S ALWAYS SUNNY IN PHILADELPHIA!")
    
    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming Always Sunny in Philadelphia!'))


#Koth
@bot.command(aliases = ["kingofthehill", "koth"], description = ": Plays King of the Hill seasons 1-13.")
async def playKoth(message):
    await message.channel.send("NOW PLAYING KING OF THE HILL!")
    
    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming King of the Hill!'))


#Metalocalypse
@bot.command(aliases = ["metalocalypse", "deathklok", "Metalocalypse", "Deathklok"], description = ": Plays Metalocalypse seasons 1-4.")
async def playMetalocalypse(message):
    await message.channel.send("NOW PLAYING METALOCALYPSE!")

    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming Metalocalypse!'))


#Samurai Jack
@bot.command(aliases = ["jack", "samuraijack"], description = ": Plays Samurai Jack seasons 1-5.")
async def playJack(message):
    await message.channel.send("NOW PLAYING SAMURAI JACK!")
    vlc.clear()
    vlc.add("D:\Shows\[Playlist]\Jack.xspf")
    vlc.play()

    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming Samurai Jack!'))


#Seinfeld
@bot.command(aliases = ["seinfeld", "Seinfeld"], description = ": Plays Seinfeld seasons 1-9.")
async def playSeinfeld(message):
    await message.channel.send("NOW PLAYING SEINFELD!")

    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming Seinfeld!'))


#Spongebob
@bot.command(aliases = ["spongebob", "Spongebob", "Spongebob Squarepants"], description = ": Plays Spongebob Squarepants seasons 1-10.")
async def playSpongebob(message):
    catEmoji = discord.utils.get(message.guild.emojis, name="threatencat")
    await message.channel.send("NOW PLAYING SPONGEBOB! " + str(catEmoji))
    vlc.clear()
    vlc.add("D:\Shows\[Playlist]\Spongebob.xspf")
    vlc.play()
    
    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming Spongebob!'))




########################################################################################################################


# Begin running
if __name__ == '__main__':
    info("Connecting to Discord...")
    bot.run(config.discord.bot_token)
