import discord
import re
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('$jarvis'):
        await message.channel.send('I\'m Jarvis, a bot to help Mollo Crew members.')

    if re.match(r'.*pabli.*', message.content):
        await message.channel.send('Bueeeenas, estas hablando con Pablooo.')


client.run(DISCORD_TOKEN)