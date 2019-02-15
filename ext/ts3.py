from discord.ext import commands
from ts3_mod import server
import json
import time
import asyncio


class TS3:
    def __init__(self, bot):
        self.bot = bot
        self.config = self.load_config(self.bot.root_dir)
        self.prefix = bot.config['prefix']

    @staticmethod
    def load_config(root_dir):
        with open(root_dir + '/config/ts3.json', 'r', encoding='utf-8') as doc:
            return json.load(doc)

    @commands.group(pass_context=True)
    async def ts(self, ctx):
        """Shows a channeltree"""
        if ctx.invoked_subcommand is None:
            ts = server.TS3Server(self.config['ts3ip'], self.config['ts3port'], self.config['ts3sid'])
            ts.login(self.config['ts3user'], self.config['ts3pass'])
            ts.set_client_nick('serveradmin')
            tree = ts.built_channeltree()
            ts.logout()
            await self.bot.say(tree)

    @ts.command(pass_context=True)
    async def poke(self, ctx, user=None, message=None):
        """Pokes a user with !ts poke "<username>" "Message here" """
        author = ctx.message.author.name
        if not message:
            message = ''
        if user:
            ts = server.TS3Server(self.config['ts3ip'], self.config['ts3port'], self.config['ts3sid'])
            ts.login(self.config['ts3user'], self.config['ts3pass'])
            ts.set_client_nick(author + ' via Discord')
            cids = ts.get_clids(user)
            if cids:
                for cid in cids:
                    ts.clientpoke(cid, message)
                    ts.logout()
                    await self.bot.say('\N{OK HAND SIGN}')
            else:
                await self.bot.say('No user named %s' % user)
        else:
            await self.bot.say('Usage: {}ts poke "<username>" "Message here"'.format(self.prefix))

    @ts.command()
    async def lastseen(self, user):
        """Shows the time since a user has been seen last"""
        ts = server.TS3Server(self.config['ts3ip'], self.config['ts3port'], self.config['ts3sid'])
        ts.login(self.config['ts3user'], self.config['ts3pass'])
        ts.set_client_nick('serveradmin')
        cldbids = ts.get_dbclids(user)
        if not cldbids:
            await self.bot.say('No user with that name')
            return
        if len(cldbids) > 1:
            await self.bot.say('There is multiple clients with that name...')
            return
        cldbid = cldbids[0]
        if ts.is_online(cldbid):
            await self.bot.say('User is currently online!')
            return
        last_conn = float(ts.get_clientdbinfo(cldbid)['client_lastconnected'])
        time_since = time.strftime("%d day(s), %H hour(s) and %M minute(s)", time.gmtime(time.time() - last_conn))
        ts.logout()
        await self.bot.say('Last registered connection is {} ago'.format(time_since))

    async def afk_check(self):
        await self.bot.wait_until_ready()
        while True:
            ts = server.TS3Server(self.config['ts3ip'], self.config['ts3port'], self.config['ts3sid'])
            ts.login(self.config['ts3user'], self.config['ts3pass'])
            ts.move_afk(self.config['afk_timeout'], self.config['afk_channel_id'])
            ts.logout()
            await asyncio.sleep(60)


def setup(bot):
    t = TS3(bot)
    bot.loop.create_task(t.afk_check())
    bot.add_cog(t)

