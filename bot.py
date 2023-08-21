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

@bot.slash_command(name="play",description="Play a song in your voice channel.",guild_only=True)
@discord.option("name",str,description="Search for a name or send a YouTube link.",required=True)
@commands.cooldown(1, 3, commands.BucketType.user)
async def _play(ctx,name=None):
    await ctx.defer()
    msg = await ctx.respond("Please wait...")

    #= ERRORS =#:
    if not name:
        return await msg.edit(content="You have not typed the name of the song you want to play.")

    if not ctx.author.voice:
        return await msg.edit(content="You are not in the voice channel. You need to be in a voice channel to use this command.")

    bot_permissions = ctx.author.voice.channel.permissions_for(ctx.guild.get_member(bot.user.id))
    if not bot_permissions.connect:
        return await msg.edit(content=f"The bot doesn't have permission to join the voice channel <#{ctx.author.voice.channel.id}>.")

    if not bot_permissions.speak:
        return await msg.edit(content=f"The bot doesn't have permission to speak/talk in the voice channel <#{ctx.author.voice.channel.id}>.")

    bot_voice = ctx.author.guild.voice_client
    if bot_voice is None or not bot_voice.is_connected():
        await ctx.author.voice.channel.connect()

    song_info = await search_youtube(name+config.search_fix)
    song_info['ask'] = ctx.author.id

    bot_voice = ctx.author.guild.voice_client
    if ctx.author.voice.channel.id != bot_voice.channel.id:
        return await msg.edit(content=f"The bot is in the voice channel <#{voice_channel.channel.id}>. You need to be in the same voice channel as the bot to use that command.")

    embed = await create_embed_play(song_info)
    embed, title = embed[0], embed[1]

    bot_voice.play(discord.FFmpegPCMAudio(song_info['url'], options='-vn'))
    return await msg.edit(content="",embed=embed)


bot.run(config.dc_token)