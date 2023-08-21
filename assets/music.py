import youtube_dl
import discord
import datetime

from assets.config import *

async def convert_minutes(sec):
    hour = sec // 3600
    minutes = (sec % 3600) // 60
    seconds = sec % 60
    return hour, minutes, seconds

async def create_embed_play(data):
    duration = await convert_minutes(data['duration'])
    if duration[0] == 0:
        duration = f"{duration[1]:02d}:{duration[2]:02d}"
    else:
        duration = f"{duration[0]:02d}:{duration[1]:02d}:{duration[2]:02d}"
    embed = discord.Embed(title='Song found!', description=f'```css\n{data["uploader"].replace(" - Topic","")} - {data["title"]}\n```',color=config.embed_color,timestamp=datetime.datetime.utcnow())
    embed.add_field(name='Duration', value=duration)
    embed.add_field(name='Ask', value=f"<@{data['ask']}>")
    embed.add_field(name='Uploaded by', value=f'[{data["uploader"]}]({data["uploader_url"]})')
    embed.add_field(name='URL', value=f'[Youtube]({data["url"]})')
    embed.set_thumbnail(url=data['thumbnail'])

    return [embed,f"{data['uploader'].replace(' - Topic','')} - {data['title']}"]

async def search_youtube(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0'
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        url = None
        if 'entries' in info:
            info = info['entries'][0]
        else:
            return None
        return info