import asyncio
import datetime
import json
import logging
import os
import sys
import traceback

import discord
from discord.ext import commands


class Bot(commands.Bot):
    def __init__(self, config_name):
        self.workdir = os.path.dirname(os.path.abspath(__file__))
        self.config = self.load_config(config_name)

        super().__init__(
                        command_prefix=commands.when_mentioned_or(self.config['prefix']),
                        description=self.config['description']
                        )

        self.start_time = None
        self.loop.create_task(self.track_start())
        self.loop.create_task(self.load_all_extensions())
        self.loop.create_task(self.help_status())

    def load_config(self, config_name):
        with open(self.workdir + config_name, 'r', encoding='utf-8') as doc:
            return json.load(doc)

    async def run(self):
        try:
            await self.start(self.config['token'], reconnect=True)
        except KeyboardInterrupt:
            await self.logout()

    async def track_start(self):
        """
        Waits for the bot to connect to discord and then records the time.
        """
        await self.wait_until_ready()
        self.start_time = datetime.datetime.utcnow()

    async def load_all_extensions(self):
        """
        Attempts to load all .py files in /ext/ as cog extensions
        """
        await self.wait_until_ready()
        await asyncio.sleep(1)  # ensure that on_ready has completed and finished printing
        #exts = [x.stem for x in Path('ext').glob('*.py')]
        exts = [x.split('.')[0] for x in os.listdir(self.workdir + '/ext') if x.endswith(".py")]

        for e in self.config['disabled_exts'].split(","):
            if e in exts:
                exts.remove(e)

        log = '\nLoading extensions:\n'
        for extension in exts:
            try:
                self.load_extension(f'ext.{extension}')
                log += '- {}\n'.format(extension)
            except Exception as e:
                error = f'{extension}\n {type(e).__name__} : {e}'
                log += '- FAILED to load extension {}\n'.format(error)
        log += '------------------------'
        logging.log(20, log)

    async def on_ready(self):
        """
        This event is called every time the bot connects or resumes connection.
        """
        connected_servers = ''
        for server in self.servers:
            connected_servers += '- {} ({})\n'.format(server, server.id)
        login_info = '\n' \
                     '------------------------\n' \
                     'Logged in as       : {} (ID {}) \n' \
                     'discord.py version : {} \n' \
                     'Start time         : {} \n' \
                     '------------------------\n' \
                     'Connected servers:\n' \
                     '{}' \
                     '------------------------' \
                     ''.format(self.user.name, self.user.id,
                               discord.__version__,
                               self.start_time,
                               connected_servers)
        logging.log(20, login_info)

    async def help_status(self):
        await self.wait_until_ready()
        await self.change_presence(game=discord.Game(name='Type {}help'.format(self.config['prefix'])))

    async def on_message(self, message):
        """
        This event triggers on every message received by the bot. Including one's that it sent itself.
        """
        if message.author.bot:
            return  # ignore all bots
        await self.process_commands(message)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    bot = Bot('/config/main.json')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot.run())
