# Discord
import discord
from discord.ext import commands, tasks

# Assets
from assets.config import *

bot = commands.Bot()

@bot.event
async def on_ready():
    print(config.on_ready.msg)


bot.run(config.dc_token)