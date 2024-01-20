import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

import discord
import youtube_dl

# from discord.ext import commands

# Suppress noise about console usage from errors
# youtube_dl.utils.bug_reports_message = lambda: ''

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    # 'quiet': True,
    # 'no_warnings': True,
    # 'default_search': 'auto',
    # 'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

voice_clients = {}

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(msg):

    if msg.content.startswith('$play'):
        try:
            # Contectar el bot al canal
            print(msg.author.voice)
            if msg.author.voice is None or msg.author.voice.channel is None:
                await msg.channel.send('Es necesario estar conectado a una sala de voz')
                return
            
            voice_client = await msg.author.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client
        except Exception as err:
            print('Error $play[1]:', err)

        try:
            url = msg.content.split()[1]
            loop = asyncio.get_event_loop()
            # data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))


            # song = data.get('url')
            player = discord.FFmpegPCMAudio(url, **ffmpeg_options)

            voice_clients[msg.guild.id].play(player)

        except Exception as err:
            print('Error $play[2]:', err)

        
    elif msg.content.startswith('$pause'):
        try:
            voice_clients[msg.guild.id].pause()
        except Exception as err:
            print(err)

    elif msg.content.startswith('$resume'):
        try:
            voice_clients[msg.guild.id].resume()
        except Exception as err:
            print(err)

    elif msg.content.startswith('$stop'):
        try:
            voice_clients[msg.guild.id].stop()
            await voice_clients[msg.guild.id].disconnect()
        except Exception as err:
            print(err)

client.run(DISCORD_TOKEN)