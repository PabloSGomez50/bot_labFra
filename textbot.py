import discord
import re
import os
import asyncio
import logging
from discord.utils import get
# import tracemalloc
from dotenv import load_dotenv
# tracemalloc.start(10)
load_dotenv()
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
log = logging.getLogger('uvicorn')
# log = 
# log.setLevel(logging.INFO)

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
SERVER_ID = int(os.getenv('SERVER_ID', 0))
BOT_CHANNEL_ID = int(os.getenv('BOT_CHANNEL_ID', 0))
ONLY_BOT_CHANNEL = bool(os.getenv('ONLY_BOT_CHANNEL', 0))

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class LabBot(discord.Client):

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

    async def on_ready(self):
        self.server_guild = self.get_guild(SERVER_ID)
        self.all_channels = self.server_guild.channels
        self.bot_channel = [c for c in self.all_channels if c.id == BOT_CHANNEL_ID][0]
        log.info(f'We have logged in as {self.user}')

    async def on_message(self, message):
        # Checkeo de canal
        if message.channel.id != self.bot_channel.id:
            return 

        if message.author.name == 'pabl1':
            log.info(f'content: {message.content}')
            log.info(f'channel: {message.channel}')

        if message.author == self.user:
            return

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




async def start_bot():
    await asyncio.create_task(client.run(DISCORD_TOKEN))
# client.run(DISCORD_TOKEN)

if __name__ == '__main__':
    client = LabBot(intents=intents)
    client.run(DISCORD_TOKEN)