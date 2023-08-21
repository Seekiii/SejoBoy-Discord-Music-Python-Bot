# Discord
import discord
from discord.ext import commands, tasks

# Assets
from assets.config import *
from assets.music import *
from assets.logs import *

bot = commands.Bot()

@bot.event
async def on_ready():
    print(config.on_ready_msg)


bot.run(config.dc_token)