import os

import discord
from discord.ext import commands

import vlc
from python_telnet_vlc import VLCTelnet

import PlaylistUtils

from modules import config_parser
from modules.logs import *

from enum import Enum
import random
import time



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
    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Game(name=f'Loambot set to kill.'))
    info(f'Successfully logged in and booted...!\n')




############################################################################################################
# General Commands
############################################################################################################


# Help command 
@bot.command(aliases = ["help"], description = ": Chooses a playlist from list of shows based on user argument and plays it.")
async def commands(message):
    cmdMsg = PlaylistUtils.commandGenerate()
    await message.channel.send(cmdMsg)


@bot.command(aliases = ["tvguide", "list"], description = ": Randomly selects a new playlist to play.")
async def listChannels(ctx):
    data = config.libraries.shows_library
    
    paginateView = PlaylistUtils.PaginationView()   
    paginateView.data = data
    await paginateView.send(ctx)



    

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
        await message.channel.send("NOW PLAYING " + PlaylistUtils.iterShowEnum(arg).upper())
        # Change bot's status to reflect new playlist
        await bot.change_presence(status=discord.Status.online,
                                activity=discord.Game(name=f'Now streaming ' + PlaylistUtils.iterShowEnum(arg)))
        
    # No playlist found; play the master playlist
    else:
        vlc.clear()
        playlist = "D:\Shows\[Playlists]\\[all].xspf"
        vlc.add(playlist)
        vlc.play()
        # Announce it
        await message.channel.send("NOW PLAYING WHATEVER COMES TO MIND!")
        # Change bot's status to reflect new playlist
        await bot.change_presence(status=discord.Status.online,
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
    showList = list(PlaylistUtils.showPlaylistToTitle)
    randomSelect = str(random.choice(showList))[20:]

    # Send message
    emoji = discord.utils.get(message.guild.emojis, name="spaghettishake")
    await message.channel.send("Gimme the remote. I'm changing the channel. " + str(emoji) )

    # Play the playlist
    vlc.clear()
    playlist = "D:\Shows\[Playlists]\\" + randomSelect + ".xspf"
    vlc.add(playlist)
    vlc.play()

    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.online,
                            activity=discord.Game(name=f'Now streaming ' + PlaylistUtils.iterShowEnum(randomSelect)))


######################################################################
# COMMANDS FOR PLAYING A PLAYLIST
#######################################################################

#Adventure Time
@bot.command(aliases = ["adventuretime", "adventure"], description = ": Plays Adventure Time seasons 1-10.")
async def playAdventureTime(message):
    playShow(message, "adventuretime") 


#Amphibia
@bot.command(aliases = ["amphibia"], description = ": Plays Amphibia seasons 1-3.")
async def playAmphibia(message):
    playShow(message, "amphibia") 


#Big City Greens
@bot.command(aliases = ["bigcitygreens"], description = ": Plays Big City Greens seasons 1-3.")
async def playBigCityGreens(message):
    playShow(message, "bigcitygreens") 


#Beavis and Butthead
@bot.command(aliases = ["beavisbutthead", "score"], description = ": Plays Beavis and Butthead seasons 1-7.")
async def playBeavisAndButthead(message):
    playShow(message, "beavisbutthead") 

    
#Boondocks
@bot.command(aliases = ["boondocks", "Boondocks", "person"], description = ": Plays The Boondocks seasons 1-4.")
async def playBoondocks(message):
    playShow(message, "boondocks") 


#Celebrity Deathmatch
@bot.command(aliases = ["cdm", "celebrity", "deathmatch"], description = ": Plays Celebrity Deathmatch seasons 1-6.")
async def playCdm(message):
    playShow(message, "cdm") 


#Chowder
@bot.command(aliases = ["chowder"], description = ": Plays Chowder seasons 1-3.")
async def playChowder(message):
    playShow(message, "chowder") 
    

#Courage
@bot.command(aliases = ["courage", "Courage", "couragethecowardlydog", "stupiddog"], description = ": Plays Courage the Cowardly Dog seasons 1-4.")
async def playCourage(message):
    playShow(message, "courage") 
    
    
#Duck Dodgers
@bot.command(aliases = ["dodgers", "duckdodgers"], description = ": Plays Duck Dodgers seasons 1-3.")
async def playDodgers(message):
    playShow(message, "duckdodgers") 


#Ed, Edd n' Eddy
@bot.command(aliases = ["ed", "eds", "ededdeddy", "canadians"], description = ": Plays Ed, Edd n' Eddy seasons 1-6.")
async def playEds(message):
    playShow(message, "eds") 


#Fresh Prince
@bot.command(aliases = ["will", "belair", "freshprince", "freshprinceofbelair"], description = ": Plays Fresh Prince of Bel-Air seasons 1-6.")
async def playFreshPrince(message):
    playShow(message, "freshprince") 


#Futurama
@bot.command(aliases = ["futurama", "Futurama"], description = ": Plays Futurama seasons 1-7.")
async def playFuturama(message):
    playShow(message, "futurama") 


#Inside Job
@bot.command(aliases = ["insidejob"], description = ": Plays Inside Job seasons 1-2.")
async def playInsideJob(message):
    playShow(message, "insidejob") 


#It's Always Sunny in Philadelphia
@bot.command(aliases = ["alwayssunny", "philly", "sunny"], description = ": Plays It's Always Sunny In Philadelphia seasons 1-13.")
async def playPhilly(message):
    playShow(message, "sunny") 


#King of the Hill
@bot.command(aliases = ["kingofthehill", "koth"], description = ": Plays King of the Hill seasons 1-13.")
async def playKoth(message):
    playShow(message, "koth") 


#Medabots
@bot.command(aliases = ["medabots"], description = ": Plays Medabots seasons 1-2")
async def playMedabots(message):
    playShow(message, "medabots") 


#Metalocalypse
@bot.command(aliases = ["metalocalypse", "deathklok"], description = ": Plays Metalocalypse seasons 1-4.")
async def playMetalocalypse(message):
    playShow(message, "metalocalypse") 


#Samurai Jack
@bot.command(aliases = ["jack", "samuraijack"], description = ": Plays Samurai Jack seasons 1-5.")
async def playJack(message):
    playShow(message, "jack") 
    

#Regular Show
@bot.command(aliases = ["regularshow", "regular"], description = ": Plays Regular Show seasons 1-3.")
async def playRegularShow(message):
    playShow(message, "regularshow") 


#Ren and Stimpy
@bot.command(aliases = ["renstimpy", "youidiot"], description = ": Plays Ren and Stimpy seasons 1-5.")
async def playRenStimpy(message):
    playShow(message, "renstimpy") 


#Seinfeld
@bot.command(aliases = ["seinfeld", "Seinfeld"], description = ": Plays Seinfeld seasons 1-9.")
async def playSeinfeld(message):
    playShow(message, "seinfeld")


#Sifl and Olly
@bot.command(aliases = ["siflolly", "socks"], description = ": Plays Sifl and Olly seasons 1-3")
async def playSiflOlly(message):
    playShow(message, "siflolly") 


#Spongebob Squarepants
@bot.command(aliases = ["spongebob", "Spongebob", "Spongebob Squarepants"], description = ": Plays Spongebob Squarepants seasons 1-10.")
async def playSpongebob(message):
    playShow(message, "spongebob") 


#Transformers Armada
@bot.command(aliases = ["transformersarm", "armada"], description = ": Plays Transformers Armada")
async def playTransArm(message):
    playShow(message, "transformersarm") 


#Sifl and Olly
@bot.command(aliases = ["transformersrid", "rid"], description = ": Plays Transformers Robots in Disguise")
async def playTransRid(message):
    playShow(message, "transformersrid") 


#Zim
@bot.command(aliases = ["zim", "invaderzim"], description = ": Plays Invader Zim.")
async def playZim(message):
    playShow(message, "zim") 


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
