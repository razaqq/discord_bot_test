import discord
from discord.ext import commands
import traceback
from prettytable import PrettyTable
import os
import logging
import requests


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.main_config = bot.config.MAIN
        self.admins = bot.config.ADMIN.admins

    def is_admin(self, user):
        if user.id in self.admins:
            return True
        else:
            return False

    @commands.group(hidden=True, pass_context=True)
    async def exts(self, ctx):
        if ctx.invoked_subcommand is None:
            t = PrettyTable()

            all_exts = [x.split('.')[0] for x in os.listdir(self.bot.root_dir + '/ext') if x.endswith(".py")]
            loaded_exts = [str(ext.split('.')[1]) for ext in self.bot.extensions.keys()]

            for ext in all_exts:
                if ext in self.main_config.enabled_exts:
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
            await ctx.send(f'```{t.get_string(sortby="Extension")}```')

    @exts.command(pass_context=True, hidden=True)
    async def enable(self, ctx, module=None):
        """Tries to enable an module."""
        author = ctx.message.author
        if self.is_admin(author):
            if not module:
                return await ctx.send('Please specify a module')
            try:
                self.bot.load_extension(f'ext.{module}')
                self.main_config.enabled_exts.append(str(module))
                self.bot.config.save()
            except commands.ExtensionNotFound:
                return await ctx.send('There is no ext with that name')
            except commands.ExtensionAlreadyLoaded:
                return await ctx.send('This ext is already enabled')
            except commands.NoEntryPointError:
                return await ctx.send('That ext has no setup function')
            except commands.ExtensionFailed as e:
                await ctx.send('Something went wrong trying to enable ext:')
                return await ctx.send(f'```py\n{traceback.format_exc()}\n```')
            else:
                await ctx.send('\N{OK HAND SIGN}')
                logging.log(20, f'Ext "{module}" was successfully enabled by {author.name}')
        else:
            await ctx.send("You don't have permissions")

    @exts.command(pass_context=True, hidden=True)
    async def disable(self, ctx, module=None):
        """Tries to disable an module."""
        author = ctx.message.author
        if self.is_admin(author):
            if not module:
                return await ctx.send('Please specify a module')
            try:
                self.bot.unload_extension(f'ext.{module}')
                self.main_config.enabled_exts.remove(str(module))
                self.bot.config.save()
            except commands.ExtensionNotLoaded:
                return await ctx.send('There is no ext enabled with that name')
            else:
                await ctx.send('\N{OK HAND SIGN}')
                logging.log(20, f'Ext "{module}" was successfully disabled by {author.name}')
        else:
            await ctx.send("You don't have permissions")

    @exts.command(pass_context=True, name='reload', hidden=True)
    async def _reload(self, ctx, module=None):
        """Reloads a module."""
        author = ctx.message.author
        if self.is_admin(author):
            if not module:
                return await ctx.send('Please specify a module')
            try:
                self.bot.reload_extension(f'ext.{module}')
            except commands.ExtensionNotLoaded:
                return await ctx.send('There is no ext enabled with that name')
            except commands.ExtensionNotFound:
                return await ctx.send('There is no ext with that name')
            except commands.NoEntryPointError:
                return await ctx.send('That ext has no setup function')
            except commands.ExtensionFailed as e:
                await ctx.send('Something went wrong trying to enable ext:')
                await ctx.send(f'```py\n{traceback.format_exc()}\n```')
            else:
                await ctx.send('\N{OK HAND SIGN}')
                logging.log(20, f'Ext {module} was successfully reloaded by {author.name}')
        else:
            await ctx.send("You don't have permissions")

    @commands.command(pass_context=True, hidden=True)
    async def shutdown(self, ctx):
        """Exits the bot with status 0 or 400"""
        author = ctx.message.author
        if self.is_admin(author):
            await ctx.send('Shutdown pending... (trying to kill all running tasks)')
            logging.log(20, f'Shutdown ordered by {author.name}')
            await self.bot.shutdown(restart=False)
        else:
            await ctx.send("You don't have permissions")

    @commands.command(pass_context=True, hidden=True)
    async def restart(self, ctx):
        """Exits the bot with status 0 or 400"""
        author = ctx.message.author
        if self.is_admin(author):
            await ctx.send('Restart pending... (trying to kill all running tasks)')
            logging.log(20, f'Restart ordered by {author.name}')
            await self.bot.shutdown(restart=True)
        else:
            await ctx.send("You don't have permissions")

    @commands.group(pass_context=True, hidden=True)
    async def presence(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid presence command passed...')

    @presence.command(pass_context=True)
    async def rename(self, ctx, *, name=None):
        if not name:
            return await ctx.send('A man must have a name')
        try:
            await self.bot.user.edit(username=name.strip())
            await ctx.send('\N{OK HAND SIGN}')
            logging.info(f'Nickname changed to "{name}" by {ctx.message.author.name}')
        except discord.HTTPException as e:
            await ctx.send(f'Failed to rename: {e}')
            logging.error(traceback.format_exc())
        except discord.ClientException:
            await ctx.send('Password required')
            logging.error(traceback.format_exc())

    @presence.command(pass_context=True)
    async def avatar(self, ctx, url):
        response = requests.get(url)
        try:
            await self.bot.user.edit(avatar=response.content)
            await ctx.send('\N{OK HAND SIGN}')
        except discord.HTTPException as e:
            await ctx.send(f'Failed change avatar: {e}')
            logging.error(traceback.format_exc())
        except discord.InvalidArgument:
            await ctx.send('Wrong image format, allowed: `.jpg` and `.png`')
            logging.error(traceback.format_exc())
        except discord.ClientException:
            await ctx.send('Password required')
            logging.error(traceback.format_exc())

    @presence.command(pass_context=True, enabled=False, hidden=True, no_pm=True)
    async def game(self, ctx, *, game=None):
        author = ctx.message.author
        if self.is_admin(author):
            if game:
                game = game.strip()
                await self.bot.change_presence(game=discord.Game(name=game))
                logging.log(20, f'Status set to "{game}" by owner')
            else:
                await self.bot.change_presence(game=None)
                logging.log(20, f'Status cleared by {author.name}')
                await ctx.send('\N{OK HAND SIGN}')
        else:
            await ctx.send("You don't have permissions")


def setup(bot):
    bot.add_cog(Admin(bot))
