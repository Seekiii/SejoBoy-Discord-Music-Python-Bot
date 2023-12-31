# Discord
import discord
from discord.ext import commands, tasks

import datetime
import asyncio

# Assets
from assets.config import *
from assets.music import *
from assets.logs import *

bot = commands.Bot()

queue = []

@bot.event
async def on_ready():
    print(config.on_ready_msg)
    queue_start.start()

@tasks.loop(seconds = 5)
async def queue_start():
    global queue
    if len(queue) > 1:
        current = queue[0]
        _next = queue[1]
        if not current['voice'].is_playing():
            current['voice'].play(discord.FFmpegPCMAudio(_next['url'], options='-vn'))
            del queue[0]

@bot.slash_command(name="play",description="Play a song in your voice channel.",guild_only=True)
@discord.option("name",str,description="Search for a name or send a YouTube link.",required=True)
@commands.cooldown(1, 3, commands.BucketType.user)
async def _play(ctx,name=None):
    global queue
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
    if not song_info['url']:
        return await msg.edit(content=f"Sorry, but we cannot find the song. Please try again with a different name.")

    bot_voice = ctx.author.guild.voice_client
    if not ctx.author.voice or not ctx.author.voice.channel or ctx.author.voice.channel.id != bot_voice.channel.id:
        return await msg.edit(content=f"The bot is in the voice channel <#{bot_voice.channel.id}>. You need to be in the same voice channel as the bot to use that command.")

    if len(queue) == 0:
        embed = await create_embed_play(song_info)
        embed, title = embed[0], embed[1]
        bot_voice.play(discord.FFmpegPCMAudio(song_info['url'], options='-vn'))
    else:
        embed = await create_embed_play(song_info,queue=True)
        embed, title = embed[0], embed[1]
    queue.append({"title":title,"embed":embed,"url":song_info['url'],"voice":bot_voice,"img":song_info['thumbnail']})
    return await msg.edit(content="",embed=embed)

@bot.slash_command(name="stop",description="Stop a song in your voice channel.",guild_only=True)
async def _stop(ctx):
    await ctx.defer()
    msg = await ctx.respond("Please wait...")

    bot_voice = ctx.author.guild.voice_client
    if bot_voice is None or not bot_voice.is_connected():
        return await msg.edit(content=f"The bot is not connected to any voice channel.")

    if not ctx.author.voice or not ctx.author.voice.channel or ctx.author.voice.channel.id != bot_voice.channel.id:
        return await msg.edit(content=f"The bot is in the voice channel <#{bot_voice.channel.id}>. You need to be in the same voice channel as the bot to use that command.")

    if bot_voice.is_playing():
        bot_voice.stop()
        await msg.edit(content=f"The bot has stopped.")
    else:
        await msg.edit(content=f"The bot isn't playing any song, and because of that, it cannot be stopped.")


@bot.slash_command(name="pause",description="Pause a song in your voice channel.",guild_only=True)
async def _pause(ctx):
    await ctx.defer()
    msg = await ctx.respond("Please wait...")

    bot_voice = ctx.author.guild.voice_client
    if bot_voice is None or not bot_voice.is_connected():
        return await msg.edit(content=f"The bot is not connected to any voice channel.")

    if not ctx.author.voice or not ctx.author.voice.channel or ctx.author.voice.channel.id != bot_voice.channel.id:
        return await msg.edit(content=f"The bot is in the voice channel <#{bot_voice.channel.id}>. You need to be in the same voice channel as the bot to use that command.")

    if bot_voice.is_playing():
        bot_voice.pause()
        await msg.edit(content=f"The bot has paused.")
    elif bot_voice.is_paused():
        await msg.edit(content=f"The bot has already paused.")
    else:
        await msg.edit(content=f"The bot isn't playing any song, and because of that, it cannot be paused.")

@bot.slash_command(name="resume",description="Resume a song in your voice channel.",guild_only=True)
async def _resume(ctx):
    await ctx.defer()
    msg = await ctx.respond("Please wait...")

    bot_voice = ctx.author.guild.voice_client
    if bot_voice is None or not bot_voice.is_connected():
        return await msg.edit(content=f"The bot is not connected to any voice channel.")

    if not ctx.author.voice or not ctx.author.voice.channel or ctx.author.voice.channel.id != bot_voice.channel.id:
        return await msg.edit(content=f"The bot is in the voice channel <#{bot_voice.channel.id}>. You need to be in the same voice channel as the bot to use that command.")

    if bot_voice.is_paused():
        bot_voice.resume()
        await msg.edit(content=f"The bot has resumed.")
    elif bot_voice.is_playing():
        await msg.edit(content=f"The bot has already resumed.")
    else:
        await msg.edit(content=f"The bot isn't playing any song, and because of that, it cannot be resumed.")

@bot.slash_command(name="queue",description="See the queue list of songs in your voice channel.",guild_only=True)
async def _queue(ctx):
    await ctx.defer()
    msg = await ctx.respond("Please wait...")

    queue_string = ""
    if len(queue) > 0:
        for num in range(len(queue)):
            song = queue[num]
            if num == 0:
                queue_string += f"[ **NOW** ] - {song['title']}\n"
            else:
                queue_string += f"[ **{num}** ] - {song['title']}\n"
        embed = discord.Embed(title='Queue', description=queue_string, color=config.embed_color['queue'], timestamp=datetime.datetime.now())
        return await msg.edit(content="", embed=embed)
    return await msg.edit(content="Queue is empty.")

@bot.slash_command(name="skip",description="Skip the current song in the voice channel.",guild_only=True)
async def _skip(ctx):
    global queue
    await ctx.defer()
    msg = await ctx.respond("Please wait...")
    if len(queue) > 1:
        bot_voice = ctx.author.guild.voice_client
        current = queue[0]
        _next = queue[1]
        if bot_voice.is_playing():
            bot_voice.stop()
        bot_voice = ctx.author.guild.voice_client
        bot_voice.play(discord.FFmpegPCMAudio(_next['url'], options='-vn'))
        del queue[0]

        embed = discord.Embed(title='Skipped', description=f"**{_next['title']}**", color=config.embed_color['skip'], timestamp=datetime.datetime.now())
        embed.set_thumbnail(url=_next['img'])
        return await msg.edit(content="", embed=embed)
    return await msg.edit(content="The song cannot be skipped because the queue is empty.")

@bot.slash_command(name="np",description="See information about the currently playing song.",guild_only=True)
async def _np(ctx):
    global queue
    await ctx.defer()
    msg = await ctx.respond("Please wait...")
    if len(queue) > 0:
        bot_voice = ctx.author.guild.voice_client
        current = queue[0]

        embed = discord.Embed(title='Now Playing', description=f"**{current['title']}**", color=config.embed_color['skip'], timestamp=datetime.datetime.now())
        embed.set_thumbnail(url=_next['img'])
        return await msg.edit(content="", embed=embed)
    return await msg.edit(content="There is no song currently playing.")

bot.run(config.dc_token)