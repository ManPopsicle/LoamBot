import os

import discord
from discord.ext import commands

from modules import config_parser
from modules.logs import *

from enum import Enum
import random
import time
import re
import csv
from tempfile import NamedTemporaryFile
import shutil


class ShowToKeyEnum(Enum):
    adventuretime = "Adventure Time"
    amphibia = "Amphibia"
    beavisbutthead = "Beavis and Buttheads"
    bigcitygreens = "Big City Greens"
    boondocks = "The Boondocks"
    cdm = "Celebrity Deathmatch"
    chowder = "Chowder"
    courage = "Courage the Cowardly Dog"
    duckdodgers = "Duck Dodgers"
    eds = "Ed Edd and Eddy"
    freshprince = "The Fresh Prince of Bel-Air"
    futurama = "Futurama"
    insidejob = "Inside Job"
    invincible = "Invincible"
    koth = "King of the Hill"
    medabots = "Medabots"
    metalocalypse = "Metalocalypse"
    regularshow = "The Regular Show"
    renstimpy = "The Ren and Stimpy Show"
    jack = "Samurai Jack"
    seinfeld = "Seinfeld"
    siflolly = "Sifl and Olly"
    spongebob = "Spongebob Squarepants"
    sunny = "It's Always Sunny In Philidelphia"
    transformersarm = "Transformers Armada"
    transformersrid = "Transformers Robots In Disguise"
    zim = "Invader Zim"

############################################################################################################
# General Commands
############################################################################################################

class PLUtils():
    
    CurrentShow = ""            # This should be a KeyName, not a ShowName value
    keyList = []
    csvName = ""
    csvPath = ""


    # This function is a replacement for DatabaseUtils' buildShowList.
    # Without a proper source that maps keynames to full names,
    # A list of the full names needs to be built by hardcoding the mapping together
    # This function will return a list of lists, organized as [ShowName, KeyName]
    # If you plan on adding more shows, you will need to add to this list
    def buildShowList(self, keyList):

        showList = []
        entryNum = 1
        for name in keyList:
            defaultTitle = "Show #" + str(entryNum)
            showEntry = [entryNum, name]
            showList.append(showEntry)
            entryNum += 1
        return showList


    # Help command 
    def commandGenerate(self, db_enabled):
        if(db_enabled):
            commandMsg = ("""```
                Available commands: 
                !play <OPTIONAL: show_name> <OPTIONAL: S##E##>: Choose a show to play. You can optionally put in the season and episode number to watch that specific episode. Otherwise, it will play a random show.
                !shuffle <on/off> : Toggles the shuffle function.
                !cc, !changechannel, !remote, !surf : Randomly changes to another playlist
                !goto <index> : Skip to an exact episode. Currently just accepts an index number of the playlist.
                !next, !skip : Go to the next episode
                !prev, !previous, !back, !goback : Go back to the previous episode
                !pause : Pauses the current episode
                !resume : Resumes the current episode
                !seek <MM:SS> : Goes to a certain timestamp in the episode
                !volume <up/down> <number> : Raise or lower the volume.
                !list : Lists the available shows
                !episodes <show_name> : List out all the episodes of a show and their index number. Episode names are currently broken.
                        ```""")
        else:
            commandMsg = ("""```
                Available commands: 
                !play <show_name> <S##E##>: Choose a show to play. You can optionally put in the season and episode number to watch that specific episode.
                !shuffle <on/off> : Toggles the shuffle function.
                !cc, !changechannel, !remote, !surf : Randomly changes to another playlist
                !goto <index> : Skip to an exact episode. Currently just accepts an index number of the playlist.
                !next, !skip : Go to the next episode
                !prev, !previous, !back, !goback : Go back to the previous episode
                !pause : Pauses the current episode
                !resume : Resumes the current episode
                !seek <MM:SS> : Goes to a certain timestamp in the episode
                !volume <up/down> <number> : Raise or lower the volume.
                !list : Lists the available shows
                        ```""")
        
        return commandMsg
    

    # CSV-based version of the timestamping functionality
    # Locates and opens the timestamp CSV file, identifies the current show playing,
    # and writes to a temporary file with an updated timestamp to the correct show row
    # then overwrites the original file with the temp
    def saveShowEntry(self, episodeName, curTime_secs):
        info("saveShowEntry 1 info")
        print("saveShowEntry 1 print")
        fullPath = self.csvPath + self.csvName + ".csv"
        info("saveShowEntry 2 info")
        print("saveShowEntry 2 print")
        tempFile = NamedTemporaryFile(mode='w', delete=False, newline='')
        info("saveShowEntry 3 info")
        print("saveShowEntry 3 print")
        fields = ['ShowName', 'EpisodeName', 'Timestamp']
        info("saveShowEntry 4 info")
        print("saveShowEntry 4 print")
        # Opening timestamp file, writing new timestamp to temp file, and updating file
        info("saveShowEntry 5 info")
        print("saveShowEntry 5 print")
        with open(fullPath, 'r', newline='', encoding='utf-8') as csvFile:
            info("saveShowEntry 6 info")
            print("saveShowEntry 6 print")
            with open(fullPath + ".tmp", 'w', newline='', encoding='utf-8') as tempFile:
                info("saveShowEntry 7 info")
                print("saveShowEntry 7 print")
                reader = csv.DictReader(csvFile, fieldnames=fields, quoting=csv.QUOTE_NOTNULL)
                info("saveShowEntry 8 info")
                print("saveShowEntry 8 print")
                writer = csv.DictWriter(tempFile, fieldnames=fields, quoting=csv.QUOTE_NOTNULL)
                info("saveShowEntry 9 info")
                print("saveShowEntry 9 print")
                for row in reader:
                    info("saveShowEntry 10 info")
                    print("saveShowEntry 10 print")
                    # Entry found, update temp file
                    info("saveShowEntry 11 info")
                    print("saveShowEntry 11 print")
                    if row['ShowName'] == str(self.CurrentShow):
                        info("saveShowEntry 12 info")
                        print("saveShowEntry 12 print")
                        row['ShowName'], row['EpisodeName'], row['Timestamp'] = self.CurrentShow, episodeName, curTime_secs
                        info("saveShowEntry 13 info")
                        print("saveShowEntry 13 print")
                        row = {'ShowName': row['ShowName'], 'EpisodeName': row['EpisodeName'], 'Timestamp': row['Timestamp']}
                    info("saveShowEntry 14 info")
                    print("saveShowEntry 14 print")
                    info("writing")
                    info("saveShowEntry 15 info")
                    print("saveShowEntry 15 print")
                    info(row)
                    info("saveShowEntry 16 info")
                    print("saveShowEntry 16 print")
                    writer.writerow(row)
                    info("saveShowEntry 17 info")
                    print("saveShowEntry 17 print")
                    info("done writing")
            
        # Updating csv file by overwriting it with the temp file
        shutil.move(tempFile.name, fullPath)

    def getShowStatus(self):
        info("calling getShowStatus info")
        print("calling getShowStatus print")
        fullPath = self.csvPath + self.csvName + ".csv"

        # Opening timestamp file, writing new timestamp to temp file, and updating file
        with open(fullPath, 'r', encoding="utf-8") as csvFile:
            reader = csv.DictReader(csvFile, quoting=csv.QUOTE_NOTNULL)
            for row in reader:
                # Entry found, return its data
                info(f"row: {row}")
                print(f"row: {row}")
                info(f"CurrentShow: {str(self.CurrentShow)}")
                print(f"CurrentShow: {str(self.CurrentShow)}")
                if row.get('ShowName') == str(self.CurrentShow):
                    return row


        

############################################################################################################
# Show List Class
############################################################################################################


class PaginationView(discord.ui.View):
    CurrentPage : int = 1
    Seperator : int = 10
    DbEnabled : False

    async def send(self, ctx):
        self.message = await ctx.send(view=self)
        await self.UpdatedMessage(self.data[:self.Seperator])


    def CreateEmbed(self, data):
        embed = discord.Embed(title=f"Available Shows  Page {self.CurrentPage} / {int(len(self.data) / self.Seperator) + 1}")
        for item in data:
            if(self.DbEnabled):
                embed.add_field(name=item[0], value=item[1], inline=False)
            else:
                embed.add_field(name=item[1], value="", inline=False)
        return embed
        

    async def UpdatedMessage(self, data):
        self.UpdateButtons()
        await self.message.edit(embed=self.CreateEmbed(data), view=self)

     
    def UpdateButtons(self):
        if self.CurrentPage == 1:
            self.first_page_button.disabled = True
            self.prev_button.disabled = True
            self.first_page_button.style = discord.ButtonStyle.gray
            self.prev_button.style = discord.ButtonStyle.gray
        else:
            self.first_page_button.disabled = False
            self.prev_button.disabled = False
            self.first_page_button.style = discord.ButtonStyle.green
            self.prev_button.style = discord.ButtonStyle.primary

        if self.CurrentPage == int(len(self.data) / self.Seperator) + 1:
            self.next_button.disabled = True
            self.last_page_button.disabled = True
            self.last_page_button.style = discord.ButtonStyle.gray
            self.next_button.style = discord.ButtonStyle.gray
        else:
            self.next_button.disabled = False
            self.last_page_button.disabled = False
            self.last_page_button.style = discord.ButtonStyle.green
            self.next_button.style = discord.ButtonStyle.primary

     
    def getCurrentPageData(self):
        until_item = self.CurrentPage * self.Seperator
        from_item = until_item - self.Seperator
        if self.CurrentPage == 1:
            from_item = 0
            until_item = self.Seperator
        if self.CurrentPage == int(len(self.data) / self.Seperator) + 1:
            from_item = self.CurrentPage * self.Seperator - self.Seperator
            until_item = len(self.data)
        return self.data[from_item:until_item]


# PaginateView buttons
    @discord.ui.button(label="|<",
                       style=discord.ButtonStyle.green)
    async def first_page_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.CurrentPage = 1

        await self.UpdatedMessage(self.getCurrentPageData())

    @discord.ui.button(label="<",
                       style=discord.ButtonStyle.primary)
    async def prev_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.CurrentPage -= 1
        await self.UpdatedMessage(self.getCurrentPageData())

    @discord.ui.button(label=">",
                       style=discord.ButtonStyle.primary)
    async def next_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.CurrentPage += 1
        await self.UpdatedMessage(self.getCurrentPageData())

    @discord.ui.button(label=">|",
                       style=discord.ButtonStyle.green)
    async def last_page_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.CurrentPage = int(len(self.data) / self.Seperator) + 1
        await self.UpdatedMessage(self.getCurrentPageData())


