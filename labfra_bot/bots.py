import re
import os
import asyncio
import logging
import discord
from discord.utils import get
from discord.ext import commands
import youtube_dl

from dotenv import load_dotenv
load_dotenv(override=True)

logging.basicConfig(
    format='[%(asctime)s] %(levelname)s - %(message)s',
    level=logging.INFO,
    encoding='utf-8'
)
log = logging.getLogger('uvicorn')

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX_BOT = os.getenv('PREFIX_BOT')
SERVER_ID = int(os.getenv('SERVER_ID', 0))
BOT_CHANNEL_ID = int(os.getenv('BOT_CHANNEL_ID', 0))
ONLY_BOT_CHANNEL = bool(os.getenv('ONLY_BOT_CHANNEL', 0))

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class Bot(discord.Client):
# class Bot(commands.Bot):
    """
    Contenido de funciones que utiliza la clase LabBot
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def set_role(self, member, role_name):
        if role_name == 'none':
            await member.edit(roles=[])
        else:
            role = get(self.server_guild.roles, name=role_name)
            await member.add_roles(role)
            return [r.name for r in member.roles]

    async def search_channel(self, name):
        try:
            return [c for c in self.all_channels if c.name == name][0]
        except IndexError:
            log.info(f'Channel "{name}" not found')
            return None
        
    async def search_member(self, name):
        try:
            return [m for m in self.server_guild.members if m.name == name][0]
        except IndexError:
            log.info(f'Miembro "{name}" not found')
            return None
        
    
    # @commands.command()
    async def connect_to_channel(self, message):
        if message.author.voice is None:
            msg = f'User {message.author.name} not in voice channel'
            log.error(msg)
            await message.channel.send(msg)
            return
        try:
            channel = message.author.voice.channel
            self.voice_channel = await channel.connect()
        except Exception as e:
            self.voice_channel = None
            msg = f"Cant connect to {channel}: {e}"
            log.error(msg)
            await message.channel.send(msg)
            return


    async def play(self, message):
        try:
            url = message.content.split(' ')[1]
            log.info(f'Informacion de url: {url}')
            # return
        except IndexError:
            await message.channel.send('No se puede obtener la url del mensaje')
            return 
        if self.voice_channel is None:
            try:
                channel = message.author.voice.channel
                self.voice_channel = await channel.connect()
            except Exception as e:
                self.voice_channel = None
                msg = f"Cant connect to {channel}: {e}"
                log.error(msg)
                await message.channel.send(msg)
                return
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        if 'youtube' in url:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                audio_path = info['formats'][0]['url']
        else:
            audio_path = os.path.join(os.path.dirname(__file__), "audio", url)
        log.info(f'Utilizando path {audio_path}')
        # if os.path.exists(audio_path):
        try:
            audio_source = discord.FFmpegPCMAudio(audio_path)
            self.voice_channel.play(audio_source)
            log.info("Se ejecuto el audio")
        except Exception as e:
            msg = 'audio not found: ' + str(e)
            log.error(msg)
            await message.channel.send(msg)
            return
        # else:
        #     log.warning(f'No existe el archivo {audio_path}')

    # @commands.command()
    async def leave(self, msg):
        if self.voice_channel:
            await self.voice_channel.disconnect()
            self.voice_channel = None
        else:
            await msg.channel.send("Bot is not connected to a voice channel.")

class LabBot(Bot):
    """
    Eventos del bot de discord
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.voice_channel = None
        self.prefix = kwargs.get('prefix')

    async def on_ready(self):
        self.server_guild = self.get_guild(SERVER_ID)
        self.all_channels = self.server_guild.channels
        self.bot_channel = [c for c in self.all_channels if c.id == BOT_CHANNEL_ID][0]
        log.info(f'We have logged in as {self.user}')

    async def on_message(self, message):
        # Checkeo de canal
        if message.channel.id != self.bot_channel.id:
            return
        
        if message.content.startswith(f'{self.prefix}connect'):
            await self.connect_to_channel(message)
            return
        
        if message.content.startswith(f'{self.prefix}play'):
            await self.play(message)
            return
        if message.content.startswith(f'{self.prefix}disconnect'):
            await self.leave(message)
            return

        if message.author.name == 'pabl1':
            log.info(f'content: {message.content}')
            log.info(f'channel: {message.channel}')

        if message.author == self.user:
            return

        if hilo := re.findall(r'\$msg hilo ([\w-]+)', message.content):
            log.info(f'Ingreso a buscar hilo con {hilo}')
            channel = [c for c in self.all_channels if c.name == message.channel.name][0]
            log.info(f'Canal: {channel}')
            if len(thread := [th for th in channel.threads if th.name == hilo[0]]) > 0:
                await thread[0].send('Puedo acceder al hilo')
            else:
                await channel.send('No tengo acceso al hilo')
            log.info('Respondio')

        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')

        if message.content.startswith('$jarvis'):
            m = 'I\'m Jarvis, a bot to help Mollo Crew members.'

            await message.channel.send(m)

        if message.content.startswith('$rol miembros'):
            all_members = [m for m in self.server_guild.members]
            members_roles = [m for m in all_members if len(m.roles) > 1]
            members_without_roles = [m for m in all_members if len(m.roles) <= 1]

            m = 'Miembros con multiples roles\n- '
            m += '\n- '.join([member.name for member in members_roles])
            m += '\n\nMiembros sin roles\n- '
            m += '\n- '.join([member.name for member in members_without_roles])

            await message.channel.send(m)

        if member_match := re.findall(r'\$rol info (\w+)', message.content):
            member_name = member_match[0]
            member = await self.search_member(member_name)

            if member:
                log.info(dir(member.roles))

                await message.channel.send(member.roles)
            else:
                m = f'No se pudo encontrar al usuario {member_name}'
                await message.channel.send(m)

        if member_match := re.findall(r'\$rol add (\w+) (.+)', message.content):
            log.info(f'Match {member_match}"')
            member_name = member_match[0][0]
            rol_name = member_match[0][1]
            log.info(f'Member: {member_name} add rol "{rol_name}"')
            member = await self.search_member(member_name)

            response = await self.set_role(member, rol_name)

            await message.channel.send(str(response))

        if message.content.startswith('$roles'):
            log.info(dir(self.server_guild.roles[0]))
            m = 'Lista de miembros por roles.'
            for role in self.server_guild.roles:
                m += f'\nRole "{role.name}": {role.id} \
                    - Bot managed {role.is_bot_managed()} - Default {role.is_default()} - Managed {role.managed} \
                    - Permision {role.permissions} - {[member.name for member in role.members]}'
            await message.channel.send(m)

        if re.match(r'.*pabli.*', message.content):
            await message.channel.send('Bueeeenas, estas hablando con Pablooo.')

if __name__ == '__main__':
    client = LabBot(intents=intents, prefix=PREFIX_BOT)
    client.run(DISCORD_TOKEN)
