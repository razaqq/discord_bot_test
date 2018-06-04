import discord
from discord.ext import commands
import traceback
import json
import logging
from prettytable import PrettyTable
import os


class Admin:
    def __init__(self, bot):
        self.bot = bot
        self.config = self.bot.config
        self.admin_config = self.load_admin_config()

    def write_main_config(self):
        with open(self.bot.workdir + '/config/main.json', 'w', encoding='utf-8') as main_config:
            return json.dump(self.config, main_config, indent=2)

    def load_admin_config(self):
        with open(self.bot.workdir + '/config/admin.json', 'r', encoding='utf-8') as admin_config:
            return json.load(admin_config)

    @commands.command(pass_context=True, hidden=True)
    async def load(self, ctx, module):
        """Loads a module."""
        author_id = ctx.message.author.id
        if author_id in self.admin_config['admins']:
            try:
                self.bot.load_extension('ext.{}'.format(module))
            except Exception as e:
                await self.bot.say('```py\n{}\n```'.format(traceback.format_exc()))
            else:
                await self.bot.say('\N{OK HAND SIGN}')
        else:
            await self.bot.say("You don't have permissions")

    @commands.command(pass_context=True, hidden=True)
    async def unload(self, ctx, module):
        """Unloads a module."""
        author_id = ctx.message.author.id
        if author_id in self.admin_config['admins']:
            try:
                self.bot.unload_extension('ext.{}'.format(module))
            except Exception as e:
                await self.bot.say('```py\n{}\n```'.format(traceback.format_exc()))
            else:
                await self.bot.say('\N{OK HAND SIGN}')
        else:
            await self.bot.say("You don't have permissions")

    @commands.command(pass_context=True, name='reload', hidden=True)
    async def _reload(self, ctx, module):
        """Reloads a module."""
        author_id = ctx.message.author.id
        if author_id in self.admin_config['admins']:
            try:
                self.bot.unload_extension('ext.{}'.format(module))
                self.bot.load_extension('ext.{}'.format(module))
            except Exception as e:
                await self.bot.say('```py\n{}\n```'.format(traceback.format_exc()))
            else:
                await self.bot.say('\N{OK HAND SIGN}')
        else:
            await self.bot.say("You don't have permissions")

    @commands.command(pass_context=True, hidden=True)
    async def enable(self, ctx, module):
        """Enables a module."""
        author_id = ctx.message.author.id
        if author_id in self.admin_config['admins']:
            try:
                if str(module) in self.config['disabled_exts'].split(','):
                    disabled_exts = self.config['disabled_exts'].split(',')
                    disabled_exts.remove(str(module))
                    disabled_string = ",".join(x for x in disabled_exts)

                    self.config['disabled_exts'] = disabled_string
                    self.write_main_config()

                    self.bot.load_extension('ext.{}'.format(module))
                else:
                    return await self.bot.say("This module is not disabled currently")
            except Exception as e:
                await self.bot.say('```py\n{}\n```'.format(traceback.format_exc()))
            else:
                await self.bot.say('\N{OK HAND SIGN}')
        else:
            await self.bot.say("You don't have permissions")

    @commands.command(pass_context=True, hidden=True)
    async def disable(self, ctx, module):
        """Disables a module."""
        author_id = ctx.message.author.id
        if author_id in self.admin_config['admins']:
            try:
                if not str(module) in self.config['disabled_exts'].split(','):
                    disabled_exts = self.config['disabled_exts'].split(',')
                    disabled_exts.append(str(module))
                    disabled_string = ",".join(x for x in disabled_exts)
                    
                    self.config['disabled_exts'] = disabled_string
                    self.write_main_config()

                    self.bot.unload_extension('ext.{}'.format(module))
                else:
                    return await self.bot.say("This module is already disabled")
            except Exception as e:
                await self.bot.say('```py\n{}\n```'.format(traceback.format_exc()))
            else:
                await self.bot.say('\N{OK HAND SIGN}')
        else:
            await self.bot.say("You don't have permissions")

    @commands.command(hidden=True)
    async def exts(self):
        t = PrettyTable()

        all_exts = [x.split('.')[0] for x in os.listdir(self.bot.workdir + '/ext') if x.endswith(".py")]
        disabled_exts = self.config['disabled_exts'].split(',')
        loaded_exts = [str(ext.split('.')[1]) for ext, mod in self.bot.extensions.items()]

        for ext in all_exts:
            loaded = str(ext in loaded_exts)
            if ext in disabled_exts:
                t.add_row([ext, 'disabled', loaded])
            else:
                t.add_row([ext, 'enabled', loaded])
        
        t.left_padding_width = 0
        t.right_padding_width = 0
        # t.title =('Currently loaded extensions')
        t.align = "r"
        t.field_names = ['Extension', 'Status', 'Loaded']
        t.align = "r"
        await self.bot.say('```{}```'.format(t))


def setup(bot):
    bot.add_cog(Admin(bot))
