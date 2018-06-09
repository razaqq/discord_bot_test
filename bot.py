#!/usr/local/bin/python3

import asyncio
import datetime
import json
import logging
from logging.handlers import RotatingFileHandler
import os
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
        self.log_setup()
        self.loop.create_task(self.track_start())
        self.loop.create_task(self.load_all_extensions())
        self.loop.create_task(self.help_status())

    def load_config(self, config_name):
        with open(self.workdir + config_name, 'r', encoding='utf-8') as doc:
            return json.load(doc)

    async def run(self):
        try:
            logging.log(20, '####################################################################')
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
        exts = [x.split('.')[0] for x in os.listdir(self.workdir + '/ext') if x.endswith(".py")]

        for e in self.config['disabled_exts'].split(","):
            if e in exts:
                exts.remove(e)

        logging.log(20, 'Loading extensions:')
        for extension in exts:
            try:
                self.load_extension(f'ext.{extension}')
                logging.log(20, '- {}'.format(extension))
            except Exception as e:
                error = f'{extension}\n {type(e).__name__} : {e}'
                logging.error('- FAILED to load extension {}'.format(error))
        logging.log(20, '------------------------')

    async def on_ready(self):
        """
        This event is called every time the bot connects or resumes connection.
        """
        logging.log(20, '------------------------')
        logging.log(20, 'Logged in as       : {} (ID {})'.format(self.user.name, self.user.id))
        logging.log(20, 'discord.py version : {} '.format(discord.__version__))
        logging.log(20, 'Start time         : {} '.format(self.start_time))
        logging.log(20, '------------------------')
        logging.log(20, 'Connected servers:')
        for server in self.servers:
            logging.log(20, '- {} ({})'.format(server, server.id))
            logging.log(20, '------------------------')

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

    async def shutdown(self, restart=True):
        await self.logout()

    def log_setup(self):
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        handler = RotatingFileHandler(self.workdir + '/logs/discord_bot.log', maxBytes=100000, backupCount=5)
        formatter = logging.Formatter('%(asctime)s - %(module)-10s - %(levelname)-5s -> %(message)s',
                                      datefmt='%d-%m|%H:%M')
        handler.setFormatter(formatter)
        logger.addHandler(handler)


if __name__ == '__main__':
    bot = Bot('/config/main.json')
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(bot.run())
    except discord.LoginFailure:
        logging.error(traceback.format_exc())
    except KeyboardInterrupt:
        loop.run_until_complete(bot.logout())
    except Exception as e:
        logging.error(e)
    finally:
        loop.close()
        exit(400)
