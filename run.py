import discord
from discord.ext import commands

from modules import config_parser
from modules.logs import *

# Parse config
config = config_parser.Config(app_name="Loambot", config_path="config.yaml")

# Start logger
logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.getLevelName(config.log_level))

# Instantiate Discord bot representation
bot = commands.Bot(command_prefix=config.discord.command_prefix, intents=discord.Intents.default())

# Help command?
formatter = commands.HelpCommand(show_check_failure=False)

info("Starting application...")

# Loambot loaded to bot variable
exts = [
    "Loambot" 
]
for ext in exts:
    bot.load_extension(ext)

# Once bot is set up, it will connect to Discord, set status to idle, set its activity to "Now streaming!"
# TODO: Write a function to update activity when playlist changes
@bot.event
async def on_ready():
    info(f'\n\nLogged in as : {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Game(name=f'Now streaming! | {config.discord.bot_prefix}'))
    info(f'Successfully logged in and booted...!\n')

# Begin running
if __name__ == '__main__':
    info("Connecting to Discord...")
    bot.run(config.discord.bot_token)
