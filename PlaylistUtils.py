import os

import discord
from discord.ext import commands

from modules import config_parser
from modules.logs import *

from enum import Enum
import random
import time


class SecretCommands(Enum):
    maverick = 1
    dieoomfie = 2
    barzoople = 3
    hotchickheaven = 4
    woolsmoth = 5
    nonono = 6



############################################################################################################
# General Commands
############################################################################################################


# Help command 
def commandGenerate():
    commandMsg = ("""```
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
        !secret : ???```""")
    
    return commandMsg
  
# Random chance to get one of the secret commands
def secretGenerate():
    for item in SecretCommands:
        if random.randint(1, 150) == item.value:
            commandMsg = ("""``` Try !""" + item.name + """ ```""")
            break
        else:
            commandMsg = ("""``` That wasn't very secret, now was it? ```""")
        
    return commandMsg
  

############################################################################################################
# Show List Class
############################################################################################################


class PaginationView(discord.ui.View):
    CurrentPage : int = 1
    Seperator : int = 10

    async def send(self, ctx):
        self.message = await ctx.send(view=self)
        await self.UpdatedMessage(self.data[:self.Seperator])


    def CreateEmbed(self, data):
        embed = discord.Embed(title=f"Available Shows  Page {self.CurrentPage} / {int(len(self.data) / self.Seperator) + 1}")
        for item in data:
            embed.add_field(name=item[0], value=item[1], inline=False)
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

        


# List shows command
def channelGenerate(message):

    index = 1           # Keeps count of page

    commandMsg = ("""```
    If you wish to change to a certain show, please type !play <show> using one of the following (remember to @SandyLoamAtSea to give her suggestions!):
    - adventuretime     (Adventure Time)
    - amphibia          (Amphibia)
    - boondocks         (The Boondocks)
    - chowder           (Chowder)
    - courage           (Courage the Cowardly Dog)
    - duckdodgers       (Duck Dodgers)
    - eds               (Ed, Edd n Eddy)
    - freshprince       (The Fresh Prince of Bel-Air)
    - futurama          (Futurama)
    - insidejob         (Inside Job)
    - koth              (King of the Hill)
    - metalocalypse     (Metalocalypse)
    - regularshow       (The Regular Show)
    - renstimpy         (The Ren and Stimpy Show)
    - jack              (Samurai Jack)
    - seinfeld          (Seinfeld)
    - siflolly          (Sifl and Olly)
    - spongebob         (Spongebob Squarepants)
    - sunny             (It's Always Sunny In Philadelphia)
    - zim               (Invader Zim)
         ```""")
    
    return commandMsg
