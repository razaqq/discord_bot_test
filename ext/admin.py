import discord
from discord.ext import commands
import traceback
import json
from prettytable import PrettyTable
import os
import logging
import requests


class Admin:
    def __init__(self, bot):
        self.bot = bot
        self.config = self.bot.config
        self.admins = self.load_admin_config()

    def is_admin(self, user):
        if int(user.id) in self.admins:
            return True
        else:
            return False

    def write_main_config(self):
        with open(self.bot.root_dir + '/config/main.json', 'w', encoding='utf-8') as main_config:
            return json.dump(self.config, main_config, indent=2)

    def load_admin_config(self):
        with open(self.bot.root_dir + '/config/admin.json', 'r', encoding='utf-8') as admin_config:
            return json.load(admin_config)['admins']

    # @commands.command(pass_context=True, hidden=True)
    # async def load(self, ctx, module):
    #    """Loads a module."""
    #    author = ctx.message.author
    #    if self.is_admin(author):
    #        try:
    #            self.bot.load_extension('ext.{}'.format(module))
    #        except Exception as e:
    #            await self.bot.say('```py\n{}\n```'.format(traceback.format_exc()))
    #        else:
    #            await self.bot.say('\N{OK HAND SIGN}')
    #            logging.log(20, 'Ext {} was successfully loaded by {}'.format(module, author.name))
    #    else:
    #        await self.bot.say("You don't have permissions")

    # @commands.command(pass_context=True, hidden=True)
    # async def unload(self, ctx, module):
    #    """Unloads a module."""
    #    author = ctx.message.author
    #    if self.is_admin(author):
    #        try:
    #            self.bot.unload_extension('ext.{}'.format(module))
    #        except Exception as e:
    #            await self.bot.say('```py\n{}\n```'.format(traceback.format_exc()))
    #        else:
    #            await self.bot.say('\N{OK HAND SIGN}')
    #            logging.log(20, 'Ext {} was successfully unloaded by {}'.format(module, author.name))
    #    else:
    #        await self.bot.say("You don't have permissions")

    @commands.command(pass_context=True, name='reload', hidden=True)
    async def _reload(self, ctx, module):
        """Reloads a module."""
        author = ctx.message.author
        if self.is_admin(author):
            try:
                self.bot.unload_extension('ext.{}'.format(module))
                self.bot.load_extension('ext.{}'.format(module))
            except Exception as e:
                await self.bot.say('```py\n{}\n```'.format(traceback.format_exc()))
            else:
                await self.bot.say('\N{OK HAND SIGN}')
                logging.log(20, 'Ext {} was successfully reloaded by {}'.format(module, author.name))
        else:
            await self.bot.say("You don't have permissions")

    @commands.group(hidden=True, pass_context=True)
    async def exts(self, ctx):
        if ctx.invoked_subcommand is None:
            t = PrettyTable()

            all_exts = [x.split('.')[0] for x in os.listdir(self.bot.root_dir + '/ext') if x.endswith(".py")]
            enabled_exts = self.config['enabled_exts'].split(',')
            loaded_exts = [str(ext.split('.')[1]) for ext, mod in self.bot.extensions.items()]

            for ext in all_exts:
                loaded = str(ext in loaded_exts)
                if ext in enabled_exts:
                    if ext in loaded_exts:
                        t.add_row([ext, 'enabled'])
                    else:
                        t.add_row([ext, 'failed to load'])
                else:
                    t.add_row([ext, 'disabled'])

            t.left_padding_width = 0
            t.right_padding_width = 0
            t.align = "r"
            t.field_names = ['Extension', 'Status']
            t.align = "r"
            await self.bot.say('```{}```'.format(t.get_string(sortby="Extension")))

    @exts.command(pass_context=True, hidden=True)
    async def enable(self, ctx, module):
        """Tries to enable an module."""
        author = ctx.message.author
        if self.is_admin(author):
            try:
                enabled_exts = self.config['enabled_exts'].split(',')
                if str(module) in enabled_exts:
                    return await self.bot.say("This module is already enabled")
                else:
                    enabled_exts.append(str(module))
                    enabled_str = ",".join(x for x in enabled_exts)
                    self.config['enabled_exts'] = enabled_str
                    self.write_main_config()

                    self.bot.load_extension('ext.{}'.format(module))
            except Exception as e:
                await self.bot.say('```py\n{}\n```'.format(traceback.format_exc()))
            else:
                await self.bot.say('\N{OK HAND SIGN}')
                logging.log(20, 'Ext "{}" was successfully enabled by {}'.format(module, author.name))
        else:
            await self.bot.say("You don't have permissions")

    @exts.command(pass_context=True, hidden=True)
    async def disable(self, ctx, module):
        """Tries to disable an module."""
        author = ctx.message.author
        if self.is_admin(author):
            try:
                enabled_exts = self.config['enabled_exts'].split(',')
                if not str(module) in enabled_exts:
                    return await self.bot.say("This module is already disabled")
                else:
                    enabled_exts.remove(str(module))
                    enabled_str = ",".join(x for x in enabled_exts)
                    self.config['enabled_exts'] = enabled_str
                    self.write_main_config()

                    self.bot.unload_extension('ext.{}'.format(module))
            except Exception as e:
                await self.bot.say('```py\n{}\n```'.format(traceback.format_exc()))
            else:
                await self.bot.say('\N{OK HAND SIGN}')
                logging.log(20, 'Ext "{}" was successfully disabled by {}'.format(module, author.name))
        else:
            await self.bot.say("You don't have permissions")

    @commands.command(pass_context=True, hidden=True)
    async def shutdown(self, ctx):
        """Exits the bot with status 0 or 400"""
        author = ctx.message.author
        if self.is_admin(author):
            await self.bot.say('Shutdown pending... (trying to kill all running tasks)')
            logging.log(20, 'SHUTDOWN ORDERED BY {}'.format(author.name))
            await self.bot.shutdown(restart=False)
        else:
            await self.bot.say("You don't have permissions")

    @commands.command(pass_context=True, hidden=True)
    async def restart(self, ctx):
        """Exits the bot with status 0 or 400"""
        author = ctx.message.author
        if self.is_admin(author):
            await self.bot.say('Restart pending... (trying to kill all running tasks)')
            logging.log(20, 'RESTART ORDERED BY {}'.format(author.name))
            await self.bot.shutdown(restart=True)
        else:
            await self.bot.say("You don't have permissions")

    @commands.group(pass_context=True)
    async def presence(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.bot.say('Invalid presence command passed...')

    @presence.command()
    async def rename(self, *, name=""):
        if name == '':
            await self.bot.say('A man must have a name')
            return
        try:
            await self.bot.edit_profile(username=name.strip())
            await self.bot.say('\N{OK HAND SIGN}')
            logging.info('Nickname changed to {} by {}')
        except discord.HTTPException as e:
            await self.bot.say('Failed to rename: {}'.format(e))
            logging.error(traceback.format_exc())
        except discord.ClientException:
            await self.bot.say('Password required')
            logging.error(traceback.format_exc())

    @presence.command()
    async def avatar(self, url):
        response = requests.get(url)
        try:
            await self.bot.edit_profile(avatar=response.content)
            await self.bot.say('\N{OK HAND SIGN}')
        except discord.HTTPException as e:
            await self.bot.say('Failed change avatar: {}'.format(e))
            logging.error(traceback.format_exc())
        except discord.InvalidArgument:
            await self.bot.say('Wrong image format, allowed: JPEG & PNG')
            logging.error(traceback.format_exc())
        except discord.ClientException:
            await self.bot.say('password required')
            logging.error(traceback.format_exc())

    @presence.command(pass_context=True, enabled=False, hidden=True, no_pm=True)
    async def game(self, ctx, *, game=None):
        author = ctx.message.author
        if self.is_admin(author):
            if game:
                game = game.strip()
                await self.bot.change_presence(game=discord.Game(name=game))
                logging.log(20, 'Status set to "{}" by owner'.format(game))
            else:
                await self.bot.change_presence(game=None)
                logging.log(20, 'status cleared by {}'.format(author.name))
                await self.bot.say('\N{OK HAND SIGN}')
        else:
            await self.bot.say("You don't have permissions")


def setup(bot):
    bot.add_cog(Admin(bot))
