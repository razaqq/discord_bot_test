#!/usr/bin/env python3.7

import asyncio
import datetime
import logging
from logging.handlers import RotatingFileHandler
import os
import traceback
import discord
from platform import python_version
from discord.ext import commands
from contextlib import suppress
import sys
import time
from config import config


__min_py_version__ = '3.7.0'


class Bot(commands.Bot):
    def __init__(self):
        self.root_dir = os.path.dirname(os.path.abspath(__file__))

        # load the config
        self.config = config.Config()
        if self.config.restart_needed:
            logging.error('Something is wrong with the config, please check the logs and edit it accordingly')
            sys.exit(0)

        super().__init__(
                        command_prefix=commands.when_mentioned_or(self.config.MAIN.prefix),
                        description=self.config.MAIN.description
                        )

        self.start_time = None
        self.initialize_logger()
        self.restart = False
        self.loop.create_task(self.track_start())
        self.loop.create_task(self.load_all_extensions())
        self.activity = discord.Game(name=f'Type {self.config.MAIN.prefix}help')

    async def run(self):
        try:
            logging.log(20, '#'*70)
            await self.start(self.config.MAIN.token, reconnect=True)
        except discord.LoginFailure:
            logging.error('Cannot login with credentials provided, please check the config')
        except KeyboardInterrupt:
            await self.logout()

    async def track_start(self):
        await self.wait_until_ready()
        self.start_time = datetime.datetime.utcnow()

    async def load_all_extensions(self):
        await self.wait_until_ready()
        await asyncio.sleep(1)  # ensure that on_ready has completed and finished printing

        extensions = self.config.MAIN.enabled_exts
        logging.log(20, 'Loading extensions:')
        for ext in extensions:
            try:
                self.load_extension(f'ext.{ext}')
                logging.log(20, f'- {ext}')
            except Exception as exception:
                error = f'{ext}\n {type(e).__name__} : {exception}'
                logging.error('- FAILED to load extension {}'.format(error))
        logging.log(20, '-'*50)

    async def on_ready(self):
        logging.log(20, '-'*50)
        logging.log(20, f'Logged in as       : {self.user.name} (ID {self.user.id})')
        logging.log(20, f'discord.py version : {discord.__version__}')
        logging.log(20, f'Start time         : {self.start_time}')
        logging.log(20, '-'*50)
        logging.log(20, 'Connected guilds:')
        for guild in self.guilds:
            logging.log(20, f'- {guild} ({guild.id})')
        logging.log(20, '-'*50)

    async def on_message(self, message):
        if message.author.bot:
            return  # ignore all bots
        await self.process_commands(message)

    async def shutdown(self, restart=False):
        self.restart = restart
        await self.logout()

    def initialize_logger(self):
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        file_handler = RotatingFileHandler(os.path.join(self.root_dir, 'logs', 'discord_bot.log'),
                                           maxBytes=100000, backupCount=5)
        formatter = logging.Formatter('%(asctime)s - %(module)-13s - %(levelname)-5s -> %(message)s',
                                      datefmt='%d-%m|%H:%M')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.setFormatter(formatter)
        logger.addHandler(stdout_handler)

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f'{error}. Type `{self.config.MAIN.prefix}help` for a list of commands!')
            return

        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send('This command cannot be used in private messages.')
            return

        if self.extra_events.get('on_command_error', None):
            return

        if hasattr(ctx.command, 'on_error'):
            return

        print(f'Ignoring exception in command {ctx.command}', file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


if __name__ == '__main__':
    if python_version() < __min_py_version__:
        print(f'This bot requires python >= {__min_py_version__}')
        sys.exit(1)

    bot = Bot()
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(bot.run())
    except discord.LoginFailure:
        logging.error(traceback.format_exc())
    except KeyboardInterrupt:
        loop.run_until_complete(bot.logout())
    except ConnectionResetError:
        time.sleep(2)
    except Exception as e:
        logging.error(e)
    finally:
        pending = asyncio.all_tasks(loop)
        for task in pending:  # cancel all tasks
            task.cancel()
            with suppress(asyncio.CancelledError):
                loop.run_until_complete(task)
        loop.close()
        if bot.restart:
            sys.exit(1)
        else:
            sys.exit(0)
