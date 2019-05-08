#!/usr/local/bin/python3.7

import asyncio
import datetime
import logging
from logging.handlers import RotatingFileHandler
import os
import traceback
import discord
from discord.ext import commands
from contextlib import suppress
import sys
import time
from config import config


class Bot(commands.Bot):
    def __init__(self):
        self.root_dir = os.path.dirname(os.path.abspath(__file__))

        # load the config
        self.config = config.Config()
        if self.config.restart_needed:
            logging.error('Something is wrong with the config, please check the logs and edit it accordingly')
            self.shutdown(restart=False)

        super().__init__(
                        command_prefix=commands.when_mentioned_or(self.config.MAIN.prefix),
                        description=self.config.MAIN.description
                        )

        self.start_time = None
        self.log_setup()
        self._restart = False
        self.loop.create_task(self.track_start())
        self.loop.create_task(self.load_all_extensions())
        self.loop.create_task(self.help_status())

    async def run(self):
        try:
            logging.log(20, '####################################################################')
            await self.start(self.config.MAIN.token, reconnect=True)
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
        Tries to load all extensions in the main config enabled_exts
        """
        await self.wait_until_ready()
        await asyncio.sleep(1)  # ensure that on_ready has completed and finished printing

        exts = self.config.MAIN.enabled_exts
        logging.log(20, 'Loading extensions:')
        for ext in exts:
            try:
                self.load_extension(f'ext.{ext}')
                logging.log(20, '- {}'.format(ext))
            except Exception as e:
                error = f'{ext}\n {type(e).__name__} : {e}'
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
        logging.log(20, 'Connected guilds:')
        for guild in self.guilds:
            logging.log(20, '- {} ({})'.format(guild, guild.id))
        logging.log(20, '------------------------')

    async def help_status(self):
        await self.wait_until_ready()
        await self.change_presence(activity=(discord.Game(name='Type {}help'.format(self.config.MAIN.prefix))))

    async def on_message(self, message):
        """
        This event triggers on every message received by the bot. Including one's that it sent itself.
        """
        if message.author.bot:
            return  # ignore all bots
        await self.process_commands(message)

    async def shutdown(self, restart=False):
        self._restart = restart
        await self.logout()

    def log_setup(self):
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        file_handler = RotatingFileHandler(self.root_dir + '/logs/discord_bot.log', maxBytes=100000, backupCount=5)
        formatter = logging.Formatter('%(asctime)s - %(module)-10s - %(levelname)-5s -> %(message)s',
                                      datefmt='%d-%m|%H:%M')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.setFormatter(formatter)
        logger.addHandler(stdout_handler)

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send('{}. Use {}help for a list of commands!'.format(error, self.config.MAIN.prefix))
            return

        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send('This command cannot be used in private messages.')
            return

        if self.extra_events.get('on_command_error', None):
            return

        if hasattr(ctx.command, "on_error"):
            return

        print('Ignoring exception in command {}'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


if __name__ == '__main__':
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
        pending = asyncio.Task.all_tasks(loop)
        for task in pending:  # cancel all tasks
            task.cancel()
            with suppress(asyncio.CancelledError):
                loop.run_until_complete(task)
        loop.close()
        if bot._restart:
            os._exit(1)
        else:
            os._exit(0)
