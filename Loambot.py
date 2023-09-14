import os

import discord
from discord.ext import commands

import vlctelnet

import PlaylistUtils
import DatabaseUtils

from modules import config_parser
from modules.logs import *

from enum import Enum
import random
import datetime
import time
import csv
import re
from os import listdir
from os.path import isfile, join


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
PORTTWO = config.vlc.port + 10
vlc = vlctelnet.VLCTelnet(HOST, PASSWORD, PORT)

# Set the initial shuffle setting
vlcIsShuffled = config.vlc.shuffle
shuffle = 'on' if vlcIsShuffled else 'off'
vlc.random(False, shuffle)

# Initialize connection with local database
dbUtils = DatabaseUtils.DbUtils()

# Save the list of KeyNames 
showList = dbUtils.buildShowList()          # Contains both KeyNames and ShowNames
keyList = []                                # Contains just the KeyNames
for item in showList:
    keyList.append(item[1])
dbUtils.keyList = keyList

# Write out default path of playlist folder
defaultPlaylistPath = "D:/Shows/[Playlists]/"
defaultAnimePlaylistPath = "D:/Shows/[Playlists]/[Anime]/"


# Get current show's keyword
rawInfo = vlc.info()
# If VLC was already open and playing, get the current show
if(rawInfo):
    fileNameAndExtension = rawInfo['data']['filename']
    fileName = os.path.splitext(fileNameAndExtension)[0]
    dbUtils.CurrentShow = dbUtils.getKeyNameFromEpisodeName(fileName)
# If VLC wasn't playing anything, set show to empty
else:
    dbUtils.CurrentShow = ""

# Instantiate Discord bot representation
bot = commands.Bot(command_prefix=config.discord.bot_prefix, intents=discord.Intents.all(), help_command=None)

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


# Help command to display available commands.
# commandGenerate() generates a formatted message that is not auto-written; you will need to fill out the text yourself
@bot.command(aliases = ["help"], description = ": Chooses a playlist from list of shows based on user argument and plays it.")
async def commands(message):
    cmdMsg = PlaylistUtils.commandGenerate()
    await message.channel.send(cmdMsg)


# Lists out all the available shows, and the keyword needed to play them
# Parameters: ctx - Context view of the Discord bot. Should be auto-populated
# Returns: None, but it will produce a list in the channel of the shows currently loaded from the config
@bot.command(aliases = ["list"], description = ": Lists out the pagination view")
async def listChannels(ctx):    
    paginateView = PlaylistUtils.PaginationView()   
    paginateView.data = showList
    await paginateView.send(ctx)



# Lists out all episodes and their index to go to them directly
# Parameters: 
#   ctx - Context view of the Discord bot. Should be auto-populated
#   arg - Playlist to be listed out
# Returns: None, but it will produce a list in the channel of the shows currently loaded from the config
@bot.command(aliases = ["episodes"], description = ": Lists out the pagination view for a specific show")
async def listEpisodes(ctx, arg):    
    paginateView = PlaylistUtils.PaginationView()  
    episodeList = dbUtils.buildEpisodeList(arg) 
    paginateView.data = episodeList
    await paginateView.send(ctx)


# Helper function for retrieving necessary data to savestate the current show
# Grabs the current timestamp of the show and queries the database to retrieve the current episode
def saveCurrentShowInfo():

    # Get current time 
    vlc.pause()
    curTime_secs = vlc.get_time()
    # Get current episode
    # In case you don't remember,  episode's ObjectId can't be saved to the corresponding Show collection entry
    # because vlc.info() only offers the file name, so searching needs to be based on that 
    rawInfo = vlc.info()
    curFileName = rawInfo['data']['filename']
    curFileName = os.path.splitext(curFileName)[0]
    dbUtils.saveShowEntry(curFileName, curTime_secs)
    

# General play command for shows. Argument should be one of the names of the playlist
#TODO: Need to add a case for when users just use !play
# Parameters:
#   arg : Playlist name
@bot.command(aliases = ["play"], description = ": Chooses a playlist from list of shows based on user argument and plays it.")
async def playShow(message, arg=None, episode=None):

    # First, save the current info if there is a show currently playing
    # if(dbUtils.CurrentShow != ""):
    saveCurrentShowInfo()
    # Look for user input in the library list
    if arg in keyList:

        # Playlist found. Locate it in the file directory and play it
        dbUtils.CurrentShow = arg
        vlc.clear()
        filePathList = dbUtils.buildPlaylist(arg)
        for filePath in filePathList: 
            print(filePath)
            vlc.enqueue(filePath)
        # filePath = defaultPlaylistPath + arg +".xspf" 
        vlc.play()
        
        # Announce it
        title = dbUtils.getShowNameFromKeyName(arg)
        await message.channel.send("NOW PLAYING " + title.upper())
        # Change bot's status to reflect new playlist
        await bot.change_presence(status=discord.Status.online,
                                activity=discord.Game(name=f'Now streaming ' + title))
        
        # Allow for S##E## formatted arguments to go to specific episodes
        if(episode != None):
            # Get season number
            justSeason = re.search("S(\d+)", episode.upper()).group()
            justSeasonNum = justSeason.split("S")[1]
            if re.search("0.", justSeasonNum) != None:
                justSeasonNum = re.search("0.", justSeasonNum).group().split("0")[1]

            # Get episode number
            justEpisode = re.search("E(\d+)", episode.upper()).group()
            justEpisodeNum = justEpisode.split("E")[1]
            if re.search("0.", justEpisodeNum) != None:
                justEpisodeNum = re.search("0.", justEpisodeNum).group().split("0")[1]

            # Find the index of the episode based on season and episode number
            index = dbUtils.getIndexFromSeasonAndEpisode(arg, justSeasonNum, justEpisodeNum)
            vlc.goto(index)

        # Check if the CurrentEpisode field is empty in Shows collection
        elif(dbUtils.showsCollection.find_one({'KeyName':arg})['CurrentEpisode'] != ""):
            # Go to saved episode and timestamp
            curEpIdx = dbUtils.getCurrentEpisodeIndex()
            vlc.goto(curEpIdx)
            # Find the saved timestamp (should be in only seconds)
            time.sleep(1)
            curEpTime = dbUtils.getSeekTime(arg)
            vlc.seek(int(curEpTime))
        
    # No playlist found; play the master playlist
    else:
        vlc.clear()
        # playlist = "D:\Shows\[Playlists]\\[all].xspf"
        
        randomSelect = str(random.choice(keyList))
        vlc.add(randomSelect)
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
        await message.channel.send("Shuffle is now on. ")
        vlcIsShuffled = True 
    # If user sets shuffle off
    elif arg == "off":
        vlc.random(False)
        catEmoji = discord.utils.get(message.guild.emojis, name="imdie")
        await message.channel.send("Shuffle is now off.")
        vlcIsShuffled = False
    # If user doesn't specify, then just toggle current status
    else:
        vlc.random()
        catEmoji = discord.utils.get(message.guild.emojis, name="doghittinit")
        vlcIsShuffled = not vlcIsShuffled
        await message.channel.send("Shuffle toggled to " + str(vlcIsShuffled) + ".")


# goto command
@bot.command(aliases = ["goto"], description = ": Goes to the next episode of whatever playlist.")
async def gototime(message, episode):    

    # First check if parameter is an index or S##E## format
    isIndex = episode.isdigit() 
    if(isIndex):
        vlc.goto(int(episode))

    # Allow for S##E## formatted arguments to go to specific episodes
    else:
        # Get season number
        justSeason = re.search("S(\d+)", episode.upper()).group()
        justSeasonNum = justSeason.split("S")[1]
        if re.search("0.", justSeasonNum) != None:
            justSeasonNum = re.search("0.", justSeasonNum).group().split("0")[1]

        # Get episode number
        justEpisode = re.search("E(\d+)", episode.upper()).group()
        justEpisodeNum = justEpisode.split("E")[1]
        if re.search("0.", justEpisodeNum) != None:
            justEpisodeNum = re.search("0.", justEpisodeNum).group().split("0")[1]

        # Find the index of the episode based on season and episode number
        index = dbUtils.getIndexFromSeasonAndEpisode(dbUtils.CurrentShow, justSeasonNum, justEpisodeNum)
        vlc.goto(index)


    emoji = discord.utils.get(message.guild.emojis, name="Sandyl12Angy")
    await message.channel.send("Playing next episode.")


# Next command
@bot.command(aliases = ["next", "skip"], description = ": Goes to the next episode of whatever playlist.")
async def nextEpisode(message):
    vlc.next()
    emoji = discord.utils.get(message.guild.emojis, name="Sandyl12Angy")
    await message.channel.send("Playing next episode." )


# Previous command
@bot.command(aliases = ["prev", "previous", "back", "goback"], description = ": Goes back to the previous episode of whatever playlist.")
async def previousEpisode(message):
    vlc.prev()
    emoji = discord.utils.get(message.guild.emojis, name="SanDrill")
    await message.channel.send("Playing previous episode.")


# Pause command
@bot.command(aliases = ["pause"], description = ": Pauses current episode.")
async def pauseEpisode(message):
    vlc.pause()
    emoji = discord.utils.get(message.guild.emojis, name="SanDrill")
    await message.channel.send("Pausing.")

    
# Resume command
@bot.command(aliases = ["resume"], description = ": Resumes current episode.")
async def resumeEpisode(message):
    vlc.play()
    emoji = discord.utils.get(message.guild.emojis, name="SanDrill")
    await message.channel.send("Resuming.")


# seek command
@bot.command(aliases = ["seek"], description = ": Goes to a certain timestamp in the episode.")
async def seekTime(message, arg):
    try:
        # Convert argument to seconds
        timeObj = time.strptime(arg, '%M:%S')
        totalSecs = timeObj.tm_sec + timeObj.tm_min*60 + timeObj.tm_hour*3600

        vlc.seek(totalSecs)
        emoji = discord.utils.get(message.guild.emojis, name="wigglyloam")
        await message.channel.send("Moving to " + arg + " timestamp" )
    except:
        emoji = discord.utils.get(message.guild.emojis, name="SandyChoppa")
        await message.channel.send("Unable to seek. Please check your formatting and try again, or ping the Loambot.")


# Volume command
@bot.command(aliases = ["volume", "vol"], description = ": Changes the volume by user input (0-200).")
async def volumeControl(message, toggle, value):
    emoji = discord.utils.get(message.guild.emojis, name="Sandyl12Angy")
    if toggle == "up":
        vlc.volup(value)
        await message.channel.send("Raising volume.")
    elif toggle == "down":
        vlc.voldown(value)
        await message.channel.send("Lowering volume.")
    else:
        await message.channel.send("Unable to change volume. Please check your formatting and try again, or ping the Loambot.")


# Change Channel command
@bot.command(aliases = ["cc", "changechannel", "remote", "surf"], description = ": Randomly selects a new playlist to play.")
async def changeChannel(message):
    # Find a random playlist
    randomSelect = str(random.choice(keyList))

    # Send message
    emoji = discord.utils.get(message.guild.emojis, name="spaghettishake")
    await message.channel.send("Changing to a random show.")

    # # Play the playlist
    vlc.clear()
    filePathList = dbUtils.buildPlaylist(randomSelect)
    for filePath in filePathList: 
        vlc.enqueue(filePath)
    curShow = randomSelect
    vlc.play()

    # Change bot's status to reflect new playlist
    await bot.change_presence(status=discord.Status.online,
                            activity=discord.Game(name=f'Now streaming ' + dbUtils.getShowNameFromKeyName(randomSelect)))


########################################################################################################################
# Other stupid commands
########################################################################################################################


# Secret command generator
# @bot.command(aliases = ["secret"], description = ": Secret roll!")
# async def secretCommandGenerator(message):
#     await message.channel.send(PlaylistUtils.secretGenerate())



# Play stream command
# @bot.command(aliases = ["gamescom"], description = ": vidya.")
# async def gamescomTime(message):
#     catEmoji = discord.utils.get(message.guild.emojis, name="videogames")
#     await message.channel.send(str(catEmoji) + " Video games suck " + str(catEmoji))
#     vlc.clear()
#     vlc.add("https://video-weaver.iad03.hls.ttvnw.net/v1/playlist/CqsGpzYpzKcWmBVwh7QD0JezeM6QZgZmd5tdZl-ls08XoF1yZcl4Mg0WerqjsiQ6PPyHbxZT0zx0CAUCM60HtlzvJOu-_8_mlKrQCGrooUf5ydel0byd8FKUOFKxPAqaAp1Fk_U4a0jXp0F1we5Rmjr-f-sJyKSRGJq3rUv8bZ6JHPsr5gwOtUj8XHsjnRywJ2oJ_8MRMJZx8xT2p_58tjx-SBRWZvReJexUxLREugaBuCa3DEJqJqsuBlyPQrP1tXQ1zKJJHk9koQCHNmb_0Xc699kEACybuWkg_QzecEzoLC45OML8hiT7a4hUHuK8skIYUOStATWFr_F0K3ocOWyVk6YDbXz-IuJKa74QQlb2_rGFyiEaWHlH8Q-YCeIOaoTAfD6PTlnT66065247BMM4Fd6NLBvGyzfq4z5l6YuYSKOjm8HqHRiAMrBj-DphQn1B3x-VecVB7vJ4B1lXdMvC7rb194tIDMHiKsL2bql83w5BnY4CKVV5gzs7UfzptpgPSm1O--9ffSiMrIG527rcxFYY6VIKIf5ooCBM4wxw1ilRoSiPRgU8kqMKpUGxFo4i_0GwZ7dWVgNSGfZkS8vXEjWdgwLFU6LGWGm0DDjpWRnH6eeQJOBFEuOnpLafS63Ye6T1ps3Ny1CSWKVUd3d1xRb5iP0Tj-HaYay17AgZq-Q5TMfdkwDkdJ1x8iWq4h5yePPeJyg8TgDv1nuk0-wa3DkMd26e2-vqDvkjiNgBwhgHDkhIOZt-yNTO5Q2Up8KB3nR7t9GJtaah5CUDvzgL8aicvH3t-EWRO99DLg9QKYiM-tggudyqJuTlp_KM2nbNnzZG9_LPdnXcxx6M8VWEQ_V2d5cdyun1jtQrQ4r9abT54EbOVBRRTxpPZhm8wXZYe6Df_uvsfnwY8wWPsCkph_jaD33v2UanLqs5pqMjWJhTEv-5_VFOsgUsg7bzZY6YTVB-v5P-OCpbKGgiWqfZD4zTb6zFjClt9rmcn9W8lMtHI8O9UZ3m_E5r27FvSv1Lpsl966nvx4YnNheo-rpAu_9vJSDvyvOMxGDgAhzvxLGQeLrJv4iSTZFN4BoMEPabMOe-Qk4iBJeZIAEqCWV1LXdlc3QtMTCiAw.m3u8")
#     vlc.play()


# # Maverick command
# @bot.command(aliases = ["maverick"], description = ": Megerman.")
# async def maverickPosting(message):
#     catEmoji = discord.utils.get(message.guild.emojis, name="leadansen")
#     await message.channel.send(str(catEmoji) + " Thought-provoking " + str(catEmoji))
#     vlc.clear()
#     vlc.add("D:\Loambot Shitposting\\mav.mp4")
#     vlc.play()


# # Die command
# @bot.command(aliases = ["dieoomfie"], description = ": die")
# async def dieOomfie(message):
#     emoji = discord.utils.get(message.guild.emojis, name="gst")
#     await message.channel.send( str(emoji) )
#     vlc.pause()
#     time.sleep(3)
#     emoji = discord.utils.get(message.guild.emojis, name="cool-1")
#     await message.channel.send( "Nah, just fucking with you." + str(emoji))
#     vlc.play()

    
# #MTV
# @bot.command(aliases = ["mtv"], description = ": Plays MTV playlist.")
# async def playMtv(message):
#     catEmoji = discord.utils.get(message.guild.emojis, name="Sandrill_tears")
#     await message.channel.send("Remember when this channel used to play music? " + str(catEmoji))
#     vlc.clear()
#     vlc.add("D:\Shows\[Playlists]\mtv.xspf")
#     vlc.play()
    
#     # Change bot's status to reflect new playlist
#     await bot.change_presence(status=discord.Status.idle,
#                               activity=discord.Game(name=f'Now streaming old MTV!'))


# #No Laugh Big Bang
# @bot.command(aliases = ["bazinga", "barzoople", "zimbabwe"], description = ": FUNNY JOKE.")
# async def playBazinga(message):
#     catEmoji = discord.utils.get(message.guild.emojis, name="kurokohaha")
#     await message.channel.send(str(catEmoji) + " INSERT LAUGHTER HERE " + str(catEmoji))
#     vlc.clear()
#     vlc.add("D:\Loambot Shitposting\\Big_Bang_Theory_But_Without_the_Laugh_Track_CRINGE.mp4")
#     vlc.play()
    
#     time.sleep(3)
#     catEmoji = discord.utils.get(message.guild.emojis, name="chew")
#     await message.channel.send("(By the way, I'm too lazy to actually make it autoplay after this is over. Change the channel after you're done having a giggle) " + str(catEmoji))

#     # Change bot's status to reflect new playlist
#     await bot.change_presence(status=discord.Status.idle,
#                               activity=discord.Game(name=f'BAZINGA!'))


# #Hot Chick Heaven
# @bot.command(aliases = ["hotchickheaven"], description = ": FUNNY JOKE.")
# async def playHotChickHeaven(message):
#     catEmoji = discord.utils.get(message.guild.emojis, name="what")
#     await message.channel.send(str(catEmoji) + " Guptill Time " + str(catEmoji))
#     vlc.clear()
#     vlc.add("D:\Loambot Shitposting\\Guptill89_Presents_-_The_Top_10_Hottest_Sonic_Females.mp4")
#     vlc.play()
    
#     time.sleep(3)
#     catEmoji = discord.utils.get(message.guild.emojis, name="chew")
#     await message.channel.send("(By the way, I'm too lazy to actually make it autoplay after this is over. Change the channel after you're done having a giggle) " + str(catEmoji))

#     # Change bot's status to reflect new playlist
#     await bot.change_presence(status=discord.Status.idle,
#                               activity=discord.Game(name=f'Hot Chick Heaven!'))
    

# #Fesh Pince
# @bot.command(aliases = ["woolsmoth"], description = ": FUNNY JOKE.")
# async def playFeshPince(message):
#     catEmoji = discord.utils.get(message.guild.emojis, name="PogPrince")
#     await message.channel.send(str(catEmoji) + " Feelin' Fresh " + str(catEmoji))
#     vlc.clear()
#     vlc.add("D:\Loambot Shitposting\\Playlists\\feshpince.xspf")
#     vlc.play()
    
#     time.sleep(3)
#     catEmoji = discord.utils.get(message.guild.emojis, name="chew")
#     await message.channel.send("(By the way, I'm too lazy to actually make it autoplay after this is over. Change the channel after you're done having a giggle) " + str(catEmoji))

#     # Change bot's status to reflect new playlist
#     await bot.change_presence(status=discord.Status.idle,
#                               activity=discord.Game(name=f'Wool Smoth'))


# #Dekembe Mutombo commercial
# @bot.command(aliases = ["nonono"], description = ": FUNNY JOKE.")
# async def playMutombo(message):
#     catEmoji = discord.utils.get(message.guild.emojis, name="saywhat")
#     await message.channel.send(str(catEmoji) + "  NOT IN MY HOUSE " + str(catEmoji))
#     vlc.clear()
#     vlc.add("D:\Loambot Shitposting\\NBA_Dikembe_Mutombo_GEICO_Commercial_no_no_no_not_in_my_house.mp4")
#     vlc.play()
    
#     time.sleep(3)
#     catEmoji = discord.utils.get(message.guild.emojis, name="chew")
#     await message.channel.send("(By the way, I'm too lazy to actually make it autoplay after this is over. Change the channel after you're done having a giggle) " + str(catEmoji))

#     # Change bot's status to reflect new playlist
#     await bot.change_presence(status=discord.Status.idle,
#                               activity=discord.Game(name=f'Wool Smoth'))


########################################################################################################################


# Begin running
if __name__ == '__main__':
    info("Connecting to Discord...")
    bot.run(config.discord.bot_token)
