import os

import discord
from discord.ext import commands

import vlc
from python_telnet_vlc import VLCTelnet

from modules import config_parser
from modules.logs import *

from enum import Enum
import random
import time

class showPlaylistToTitle(Enum):
    adventuretime = "Adventure Time"
    amphibia = "Amphibia"
    boondocks = "The Boondocks"
    chowder = "Chowder"
    courage = "Courage the Cowardly Dog"
    duckdodgers = "Duck Dodgers"
    eds = "Ed, Edd n Eddy"
    freshprince = "The Fresh Prince of Bel-Air"
    futurama = "Futurama"
    insidejob = "Inside Job"
    koth = "King of the Hill"
    metalocalypse = "Metalocalypse"
    regularshow = "The Regular Show"
    renstimpy = "The Ren and Stimpy Show"
    jack = "Samurai Jack"
    seinfeld = "Seinfeld"
    siflolly = "Sifl and Olly"
    spongebob = "Spongebob Squarepants"
    sunny = "It's Always Sunny In Philadelphia"
    zim = "Invader Zim"

# Returns a properly formatted version of a show name
def iterShowEnum(listItem):
    for member in showPlaylistToTitle:
        if listItem == member.name:
            return member.value
    
    return False

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




############################################################################################################
# General Commands
############################################################################################################


# Help command 
@bot.command(aliases = ["help"], description = ": Chooses a playlist from list of shows based on user argument and plays it.")
async def commands(message):
    await message.channel.send("""```
        Available commands: 
        !play <show_name> : Choose a show to play
        !shuffle <on/off> : Toggles the shuffle function.
        !cc, !changechannel, !remote, !surf : Randomly changes to another playlist
        !next, !skip : Go to the next episode
        !prev, !previous, !back, !goback : Go back to the previous episode
        !pause : Pauses the current episode
        !resume : Resumes the current episode
        !seek <MM:SS> : Goes to a certain timestamp in the episode
        !volume <up/down> <number> : Raise or lower the volume.
        !list : Shows the available shows
        Other secret commands???
                               ```""")
  


# General play command for shows. Argument should be one of the names of the playlist
@bot.command(aliases = ["play"], description = ": Chooses a playlist from list of shows based on user argument and plays it.")
async def playShow(message, arg):
    # Look for user input in the library list
    if arg in config.libraries.shows_library:
        # Playlist found. Locate it in the file directory and play it
        vlc.clear()
        playlist = "D:\Shows\[Playlists]\\" + arg + ".xspf"
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
        playlist = "D:\Shows\[Playlists]\\[all].xspf"
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
    # If user sets shuffle on
    if arg == "on":
        vlc.random(True)
        catEmoji = discord.utils.get(message.guild.emojis, name="catrave")
        await message.channel.send(str(catEmoji) + " Shuffle is now on. " + str(catEmoji))
        vlcIsShuffled = True 
    # If user sets shuffle off
    elif arg == "off":
        vlc.random(False)
        catEmoji = discord.utils.get(message.guild.emojis, name="imdie")
        await message.channel.send(str(catEmoji) + " Shuffle is now off. " + str(catEmoji))
        vlcIsShuffled = False
    # If user doesn't specify, then just toggle current status
    else:
        vlc.random()
        catEmoji = discord.utils.get(message.guild.emojis, name="doghittinit")
        vlcIsShuffled = not vlcIsShuffled
        await message.channel.send(str(catEmoji) + " Shuffle toggled to " + str(vlcIsShuffled) + ". " + str(catEmoji))


# Next command
@bot.command(aliases = ["next", "skip"], description = ": Goes to the next episode of whatever playlist.")
async def nextEpisode(message):
    vlc.next()
    emoji = discord.utils.get(message.guild.emojis, name="Sandyl12Angy")
    await message.channel.send("This shit sucks! NEXT EPISODE. " + str(emoji) )


# Previous command
@bot.command(aliases = ["prev", "previous", "back", "goback"], description = ": Goes back to the previous episode of whatever playlist.")
async def previousEpisode(message):
    vlc.prev()
    emoji = discord.utils.get(message.guild.emojis, name="SanDrill")
    await message.channel.send("Rewind the tape! That shit was sick. " + str(emoji) )


# Pause command
@bot.command(aliases = ["pause"], description = ": Pauses current episode.")
async def pauseEpisode(message):
    vlc.pause()
    emoji = discord.utils.get(message.guild.emojis, name="SanDrill")
    await message.channel.send("Hang on, gotta take a leak. " + str(emoji) )

    
# Resume command
@bot.command(aliases = ["resume"], description = ": Resumes current episode.")
async def resumeEpisode(message):
    vlc.play()
    emoji = discord.utils.get(message.guild.emojis, name="SanDrill")
    await message.channel.send("Alright, I closed/opened the window. " + str(emoji) )


# seek command
@bot.command(aliases = ["seek"], description = ": Goes to a certain timestamp in the episode.")
async def seekTime(message, arg):
    try:
        # Convert argument to seconds
        timeObj = time.strptime(arg, '%M:%S')
        totalSecs = timeObj.tm_sec + timeObj.tm_min*60 + timeObj.tm_hour*3600

        vlc.seek(totalSecs)
        emoji = discord.utils.get(message.guild.emojis, name="wigglyloam")
        await message.channel.send("Moving to " + arg + " timestamp (hopefully)! "+ str(emoji) )
    except:
        emoji = discord.utils.get(message.guild.emojis, name="SandyChoppa")
        await message.channel.send("I don't wanna sanitize your timestamp. Please make sure it's in MM:SS. That, or something else went wrong, like the episode isn't that long or something. " + str(emoji) )


# Volume command
@bot.command(aliases = ["volume", "vol"], description = ": Changes the volume by user input (0-200).")
async def volumeControl(message, toggle, value):
    emoji = discord.utils.get(message.guild.emojis, name="Sandyl12Angy")
    if toggle == "up":
        vlc.volup(value)
        await message.channel.send(str(emoji) + "Can't hear shit!"  + str(emoji))
    elif toggle == "down":
        vlc.voldown(value)
        await message.channel.send(str(emoji) + "Keep it down!"  + str(emoji))
    else:
        await message.channel.send(str(emoji) + "Please follow the volume syntax!"  + str(emoji))


# Change Channel command
@bot.command(aliases = ["cc", "changechannel", "remote", "surf"], description = ": Randomly selects a new playlist to play.")
async def changeChannel(message):
    # Find a random playlist
    showList = list(showPlaylistToTitle)
    randomSelect = str(random.choice(showList))[20:]

    # Play the playlist
    vlc.clear()
    playlist = "D:\Shows\[Playlists]\\" + randomSelect + ".xspf"
    vlc.add(playlist)
    vlc.play()

    # Send message
    emoji = discord.utils.get(message.guild.emojis, name="spaghettishake")
    await message.channel.send("Gimme the remote. I'm changing the channel. " + str(emoji) )

    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                            activity=discord.Game(name=f'Now streaming ' + iterShowEnum(randomSelect)))


# List shows command
#TODO: Rewrite so it just pulls from the config and formats it into a list
@bot.command(aliases = ["tvguide", "list"], description = ": Randomly selects a new playlist to play.")
async def listChannels(message):
    await message.channel.send("""```
    If you wish to change to a certain show, please type !play <show> using one of the following (remember to @SandyLoamAtSea to give her suggestions!):
    - adventuretime (Adventure Time)
    - amphibia (Amphibia)
    - boondocks (The Boondocks)
    - chowder (Chowder)
    - courage (Courage the Cowardly Dog)
    - duckdodgers (Duck Dodgers)
    - eds (Ed, Edd n Eddy)
    - freshprince (The Fresh Prince of Bel-Air)
    - futurama (Futurama)
    - insidejob (Inside Job)
    - koth (King of the Hill)
    - metalocalypse (Metalocalypse)
    - regularshow (The Regular Show)
    - renstimpy (The Ren and Stimpy Show)
    - jack (Samurai Jack)
    - seinfeld (Seinfeld)
    - siflolly (Sifl and Olly)
    - spongebob (Spongebob Squarepants)
    - sunny (It's Always Sunny In Philadelphia)
    - zim (Invader Zim)
         ```""")

######################################################################
# COMMANDS FOR PLAYING A PLAYLIST
# AVAILABLE PLAYLISTS:
# - Amphibia
# - Beavis and Butthead
# - Boondocks
# - Chowder
# - Courage the Cowardly Dog
# - Duck Dodgers
# - Ed, Edd n' Eddy
# - Fresh Prince of Bel-Air
# - Futurama
# - Inside Job
# - Invader Zim
# - It's Always Sunny In Philadelphia
# - King of the Hill
# - Metalocalypse
# - Ren and Stimpy
# - Samurai Jack
# - Seinfeld
# - Sifl and Olly
# - Spongebob Squarepants
#######################################################################

#Adventure Time
@bot.command(aliases = ["adventuretime", "adventure"], description = ": Plays Adventure Time seasons 1-10.")
async def playAdventureTime(message):
    catEmoji = discord.utils.get(message.guild.emojis, name="INSANECAT")
    await message.channel.send("NOW PLAYING ADVENTURE TIME! " + str(catEmoji))
    vlc.clear()
    vlc.add("D:\Shows\[Playlists]\\adventuretime.xspf")
    vlc.play()
    
    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming Adventure Time!'))


#Amphibia
@bot.command(aliases = ["amphibia"], description = ": Plays Amphibia seasons 1-3.")
async def playAmphibia(message):
    catEmoji = discord.utils.get(message.guild.emojis, name="INSANECAT")
    await message.channel.send("NOW PLAYING AMPHIBIA! " + str(catEmoji))
    vlc.clear()
    vlc.add("D:\Shows\[Playlists]\\amphibia.xspf")
    vlc.play()
    
    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming Amphibia!'))

#Boondocks
@bot.command(aliases = ["boondocks", "Boondocks", "person"], description = ": Plays The Boondocks seasons 1-4.")
async def playBoondocks(message):
    catEmoji = discord.utils.get(message.guild.emojis, name="INSANECAT")
    await message.channel.send("NOW PLAYING THE BOONDOCKS! " + str(catEmoji))
    vlc.clear()
    vlc.add("D:\Shows\[Playlists]\\boondocks.xspf")
    vlc.play()
    
    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming The Boondocks!'))
    

#Beavis and Butthead
@bot.command(aliases = ["beavisbutthead", "score"], description = ": Plays Beavis and Butthead seasons 1-7.")
async def playBeavisAndButthead(message):
    catEmoji = discord.utils.get(message.guild.emojis, name="INSANECAT")
    await message.channel.send("NOW PLAYING BEAVIS AND BUTTHEAD! " + str(catEmoji))
    vlc.clear()
    vlc.add("D:\Shows\[Playlists]\\beavisbutthead.xspf")
    vlc.play()
    
    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming Beavis and Butthead!'))


#Celebrity Deathmatch
@bot.command(aliases = ["cdm", "celebrity", "deathmatch"], description = ": Plays Celebrity Deathmatch seasons 1-6.")
async def playCdm(message):
    catEmoji = discord.utils.get(message.guild.emojis, name="INSANECAT")
    await message.channel.send("NOW PLAYING CELEBRITY DEATHMATCH! " + str(catEmoji))
    vlc.clear()
    vlc.add("D:\Shows\[Playlists]\\cdm.xspf")
    vlc.play()
    
    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming Celebrity Deathmatch!'))


#Chowder
@bot.command(aliases = ["chowder"], description = ": Plays Chowder seasons 1-3.")
async def playChowder(message):
    catEmoji = discord.utils.get(message.guild.emojis, name="INSANECAT")
    await message.channel.send("NOW PLAYING CHOWDER! " + str(catEmoji))
    vlc.clear()
    vlc.add("D:\Shows\[Playlists]\chowder.xspf")
    vlc.play()
    
    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming Chowder!'))
    

#Courage
@bot.command(aliases = ["courage", "Courage", "couragethecowardlydog", "stupiddog"], description = ": Plays Courage the Cowardly Dog seasons 1-4.")
async def playCourage(message):
    catEmoji = discord.utils.get(message.guild.emojis, name="INSANECAT")
    await message.channel.send("NOW PLAYING COURAGE THE COWARDLY DOG! " + str(catEmoji))
    vlc.clear()
    vlc.add("D:\Shows\[Playlists]\courage.xspf")
    vlc.play()
    
    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming Courage the Cowardly Dog!'))
    
    
#Duck Dodgers
@bot.command(aliases = ["dodgers", "duckdodgers"], description = ": Plays Duck Dodgers seasons 1-3.")
async def playDodgers(message):
    catEmoji = discord.utils.get(message.guild.emojis, name="INSANECAT")
    await message.channel.send("NOW PLAYING DUCK DODGERS! " + str(catEmoji))
    vlc.clear()
    vlc.add("D:\Shows\[Playlists]\\duckdodgers.xspf")
    vlc.play()
    
    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming Duck Dodgers!'))


#Eds
@bot.command(aliases = ["ed", "eds", "ededdeddy", "canadians"], description = ": Plays Ed, Edd n' Eddy seasons 1-6.")
async def playEds(message):
    catEmoji = discord.utils.get(message.guild.emojis, name="INSANECAT")
    await message.channel.send("NOW PLAYING ED, EDD N' EDDY! " + str(catEmoji))
    vlc.clear()
    vlc.add("D:\Shows\[Playlists]\eds.xspf")
    vlc.play()
    
    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming Ed, Edd n Eddy!'))


#Fresh Prince
@bot.command(aliases = ["will", "belair", "freshprince", "freshprinceofbelair"], description = ": Plays Fresh Prince of Bel-Air seasons 1-6.")
async def playFreshPrince(message):
    catEmoji = discord.utils.get(message.guild.emojis, name="INSANECAT")
    await message.channel.send("NOW PLAYING FRESH PRINCE OF BEL-AIR! " + str(catEmoji))
    vlc.clear()
    vlc.add("D:\Shows\[Playlists]\\freshprince.xspf")
    vlc.play()
    
    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming The Fresh Prince of Bel-Air!'))


#Futurama
@bot.command(aliases = ["futurama", "Futurama"], description = ": Plays Futurama seasons 1-7.")
async def playFuturama(message):
    catEmoji = discord.utils.get(message.guild.emojis, name="INSANECAT")
    await message.channel.send("NOW PLAYING FUTURAMA! " + str(catEmoji))
    vlc.clear()
    vlc.add("D:\Shows\[Playlists]\\futurama.xspf")
    vlc.play()
    
    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming Futurama!'))


#Inside Job
@bot.command(aliases = ["insidejob"], description = ": Plays Inside Job seasons 1-2.")
async def playInsideJob(message):
    catEmoji = discord.utils.get(message.guild.emojis, name="INSANECAT")
    await message.channel.send("NOW PLAYING INSIDE JOB! " + str(catEmoji))
    vlc.clear()
    vlc.add("D:\Shows\[Playlists]\\insidejob.xspf")
    vlc.play()
    
    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming Inside Job!'))


#Always Sunny
@bot.command(aliases = ["alwayssunny", "philly"], description = ": Plays It's Always Sunny In Philadelphia seasons 1-13.")
async def playPhilly(message):
    catEmoji = discord.utils.get(message.guild.emojis, name="INSANECAT")
    await message.channel.send("NOW PLAYING IT'S ALWAYS SUNNY IN PHILADELPHIA! " + str(catEmoji))
    vlc.clear()
    vlc.add("D:\Shows\[Playlists]\sunny.xspf")
    vlc.play()
    
    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming Always Sunny in Philadelphia!'))


#Koth
@bot.command(aliases = ["kingofthehill", "koth"], description = ": Plays King of the Hill seasons 1-13.")
async def playKoth(message):
    catEmoji = discord.utils.get(message.guild.emojis, name="INSANECAT")
    await message.channel.send("NOW PLAYING KING OF THE HILL! " + str(catEmoji))
    vlc.clear()
    vlc.add("D:\Shows\[Playlists]\koth.xspf")
    vlc.play()
    
    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming King of the Hill!'))


#Metalocalypse
@bot.command(aliases = ["metalocalypse", "deathklok"], description = ": Plays Metalocalypse seasons 1-4.")
async def playMetalocalypse(message):
    catEmoji = discord.utils.get(message.guild.emojis, name="INSANECAT")
    await message.channel.send("NOW PLAYING METALOCALYPSE! " + str(catEmoji))
    vlc.clear()
    vlc.add("D:\Shows\[Playlists]\metalocalypse.xspf")
    vlc.play()

    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming Metalocalypse!'))


#Samurai Jack
@bot.command(aliases = ["jack", "samuraijack"], description = ": Plays Samurai Jack seasons 1-5.")
async def playJack(message):
    catEmoji = discord.utils.get(message.guild.emojis, name="INSANECAT")
    await message.channel.send("NOW PLAYING SAMURAI JACK! " + str(catEmoji))
    vlc.clear()
    vlc.add("D:\Shows\[Playlists]\jack.xspf")
    vlc.play()

    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming Samurai Jack!'))
    

#Regular Show
@bot.command(aliases = ["regularshow", "regular"], description = ": Plays Regular Show seasons 1-3.")
async def playRegularShow(message):
    catEmoji = discord.utils.get(message.guild.emojis, name="INSANECAT")
    await message.channel.send("NOW PLAYING REGULAR SHOW! " + str(catEmoji))
    vlc.clear()
    vlc.add("D:\Shows\[Playlists]\\regularshow.xspf")
    vlc.play()
    
    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming Regular Show!'))


#Ren and Stimpy
@bot.command(aliases = ["renstimpy", "youidiot"], description = ": Plays Ren and Stimpy seasons 1-5.")
async def playRenStimpy(message):
    catEmoji = discord.utils.get(message.guild.emojis, name="INSANECAT")
    await message.channel.send("NOW PLAYING REN AND STIMPY! " + str(catEmoji))
    vlc.clear()
    vlc.add("D:\Shows\[Playlists]\renstimpy.xspf")
    vlc.play()

    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming Ren and Stimpy!'))


#Seinfeld
@bot.command(aliases = ["seinfeld", "Seinfeld"], description = ": Plays Seinfeld seasons 1-9.")
async def playSeinfeld(message):
    catEmoji = discord.utils.get(message.guild.emojis, name="INSANECAT")
    await message.channel.send("NOW PLAYING SEINFELD! " + str(catEmoji))
    vlc.clear()
    vlc.add("D:\Shows\[Playlists]\seinfeld.xspf")
    vlc.play()

    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming Seinfeld!'))


#Sifl and Olly
@bot.command(aliases = ["siflolly", "socks"], description = ": Plays Sifl and Olly seasons 1-3")
async def playSiflOlly(message):
    catEmoji = discord.utils.get(message.guild.emojis, name="INSANECAT")
    await message.channel.send("NOW PLAYING SIFL AND OLLY! " + str(catEmoji))
    vlc.clear()
    vlc.add("D:\Shows\[Playlists]\\siflolly.xspf")
    vlc.play()
    
    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming Sifl and Olly!'))

#Spongebob
@bot.command(aliases = ["spongebob", "Spongebob", "Spongebob Squarepants"], description = ": Plays Spongebob Squarepants seasons 1-10.")
async def playSpongebob(message):
    catEmoji = discord.utils.get(message.guild.emojis, name="INSANECAT")
    await message.channel.send("NOW PLAYING SPONGEBOB! " + str(catEmoji))
    vlc.clear()
    vlc.add("D:\Shows\[Playlists]\spongebob.xspf")
    vlc.play()
    
    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming Spongebob!'))


#Zim
@bot.command(aliases = ["zim"], description = ": Plays Invader Zim.")
async def playZim(message):
    catEmoji = discord.utils.get(message.guild.emojis, name="INSANECAT")
    await message.channel.send("NOW PLAYING ZIM! " + str(catEmoji))
    vlc.clear()
    vlc.add("D:\Shows\[Playlists]\zim.xspf")
    vlc.play()
    
    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming Invader Zim!'))


########################################################################################################################
# Other stupid commands
########################################################################################################################

# Maverick command
@bot.command(aliases = ["maverick"], description = ": Megerman.")
async def maverickPosting(message):
    vlc.play()
    emoji = discord.utils.get(message.guild.emojis, name="aaaaaaaaaaaaaaaaaaa")
    await message.channel.send( str(emoji) )

# Die command
@bot.command(aliases = ["die"], description = ": die")
async def dieOomfie(message, *arg):
    emoji = discord.utils.get(message.guild.emojis, name="gst")
    await message.channel.send( str(emoji) )
    vlc.pause()
    time.sleep(3)
    emoji = discord.utils.get(message.guild.emojis, name="cool-1")
    await message.channel.send( "Nah, just fucking with you." + str(emoji))
    vlc.play()

    
#MTV
@bot.command(aliases = ["mtv"], description = ": Plays MTV playlist.")
async def playMtv(message):
    catEmoji = discord.utils.get(message.guild.emojis, name="Sandrill_tears")
    await message.channel.send("Remember when this channel used to play music? " + str(catEmoji))
    vlc.clear()
    vlc.add("D:\Shows\[Playlists]\mtv.xspf")
    vlc.play()
    
    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming old MTV!'))


#No Laugh Big Bang
@bot.command(aliases = ["bazinga", "barzoople", "zimbabwe"], description = ": FUNNY JOKE.")
async def playBazinga(message):
    catEmoji = discord.utils.get(message.guild.emojis, name="kurokohaha")
    await message.channel.send(str(catEmoji) + " INSERT LAUGHTER HERE " + str(catEmoji))
    vlc.clear()
    vlc.add("D:\Loambot Shitposting\\Big_Bang_Theory_But_Without_the_Laugh_Track_CRINGE.mp4")
    vlc.play()
    
    time.sleep(3)
    catEmoji = discord.utils.get(message.guild.emojis, name="chew")
    await message.channel.send("(By the way, I'm too lazy to actually make it autoplay after this is over. Change the channel after you're done having a giggle) " + str(catEmoji))

    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'BAZINGA!'))



#Hot Chick Heaven
@bot.command(aliases = ["hotchickheaven"], description = ": FUNNY JOKE.")
async def playHotChickHeaven(message):
    catEmoji = discord.utils.get(message.guild.emojis, name="what")
    await message.channel.send(str(catEmoji) + " Guptill Time " + str(catEmoji))
    vlc.clear()
    vlc.add("D:\Loambot Shitposting\\Guptill89_Presents_-_The_Top_10_Hottest_Sonic_Females.mp4")
    vlc.play()
    
    time.sleep(3)
    catEmoji = discord.utils.get(message.guild.emojis, name="chew")
    await message.channel.send("(By the way, I'm too lazy to actually make it autoplay after this is over. Change the channel after you're done having a giggle) " + str(catEmoji))

    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Hot Chick Heaven!'))

########################################################################################################################

# Begin running
if __name__ == '__main__':
    info("Connecting to Discord...")
    bot.run(config.discord.bot_token)
