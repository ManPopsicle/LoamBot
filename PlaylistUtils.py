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
                !play <OPTIONAL : show_name> <OPTIONAL: S##E##>: Choose a show to play. You can optionally put in the season and episode to watch that specific episode. If no arguments are given, it will play a random show.
                !shuffle : Toggles the shuffle function.
                !cc, !changechannel, !remote, !surf : Randomly changes to another playlist
                !goto <index> : Skip to an exact episode. Currently just accepts an index number of the playlist.
                !next, !skip : Go to the next episode
                !prev, !previous, !back, !goback : Go back to the previous episode
                !pause : Pauses the current episode
                !resume : Resumes the current episode
                !seek <MM:SS> : Goes to a certain timestamp in the episode
                !volume <up/down> <number> : Raise or lower the volume. The volume will raise or lower in increments of 5%, according to the input rounded to the nearest increment.
                !list, !shows : Lists the available shows
                !episodes <show_name> : List out all the episodes of a show and their index number. Episode names are currently broken.
                        ```""")
        else:
            commandMsg = ("""```
                Available commands: 
                !play <OPTIONAL: show_name> <OPTIONAL: index_number> : Choose a show to play. You can optionally input an index number to watch a specific episode. If no arguments are given, it will play a random show.
                !shuffle : Toggles the shuffle function.
                !cc, !changechannel, !remote, !surf : Randomly changes to another playlist
                !goto <index> : Skip to an exact episode. Currently just accepts an index number of the playlist.
                !next, !skip : Go to the next episode
                !prev, !previous, !back, !goback : Go back to the previous episode
                !pause : Pauses the current episode
                !resume : Resumes the current episode
                !seek <MM:SS> : Goes to a certain timestamp in the episode
                !volume <up/down> <number> : Raise or lower the volume. The volume will raise or lower in increments of 5%.
                !list, !shows : Lists the available shows
                        ```""")
        
        return commandMsg
    

    # CSV-based version of the timestamping functionality
    # Locates and opens the timestamp CSV file, identifies the current show playing,
    # and writes to a temporary file with an updated timestamp to the correct show row
    # then overwrites the original file with the temp
    def saveShowEntry(self, episodeName, curTime_secs):
        fullPath = self.csvPath + self.csvName + ".csv"
        tempFile = NamedTemporaryFile(mode='w', delete=False, newline='')
        fields = ['ShowName', 'EpisodeName', 'Timestamp']
        # Opening timestamp file, writing new timestamp to temp file, and updating file
        with open(fullPath, 'r', newline='', encoding='utf-8') as csvFile:
            with open(fullPath + ".tmp", 'w', newline='', encoding='utf-8') as tempFile:
                reader = csv.DictReader(csvFile, fieldnames=fields, quoting=csv.QUOTE_NOTNULL)
                writer = csv.DictWriter(tempFile, fieldnames=fields, quoting=csv.QUOTE_NOTNULL)
                for row in reader:
                    # Entry found, update temp file
                    if row['ShowName'] == str(self.CurrentShow):
                        row['ShowName'], row['EpisodeName'], row['Timestamp'] = self.CurrentShow, episodeName, curTime_secs
                        row = {'ShowName': row['ShowName'], 'EpisodeName': row['EpisodeName'], 'Timestamp': row['Timestamp']}
                    writer.writerow(row)
            
        # Updating csv file by overwriting it with the temp file
        shutil.move(tempFile.name, fullPath)

    def getShowStatus(self):
        fullPath = self.csvPath + self.csvName + ".csv"

        # Opening timestamp file, writing new timestamp to temp file, and updating file
        with open(fullPath, 'r', encoding="utf-8") as csvFile:
            reader = csv.DictReader(csvFile, quoting=csv.QUOTE_NOTNULL)
            for row in reader:
                # Entry found, return its data
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


