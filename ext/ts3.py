from discord.ext import commands
from ts3py.server import TS3Server
import asyncio


class TS3(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config.TS3
        self.prefix = bot.config.MAIN.prefix

    @commands.group(pass_context=True)
    async def ts(self, ctx):
        """Shows a channeltree"""
        if ctx.invoked_subcommand is None:
            ts = TS3Server(self.config.ip, self.config.port, self.config.sid)
            ts.login(self.config.user, self.config.password)
            ts.set_client_nick('serveradmin')
            tree = ts.get_channeltree()
            if not tree:
                return await ctx.send('nobody is here <:feelsbad:345232499103891456>')
            ts.logout()
            await ctx.send('```{}```'.format(tree))

    @ts.command(pass_context=True, usage='poke <user>')
    async def poke(self, ctx, user=None, message=''):
        """Pokes a user with !ts poke "<username>" "Message here" """
        author = ctx.author.name
        if user:
            ts = TS3Server(self.config.ip, self.config.port, self.config.sid)
            ts.login(self.config.user, self.config.password)
            ts.set_client_nick(author + ' via Discord')
            cids = ts.get_clids(user)
            if cids:
                for cid in cids:
                    ts.clientpoke(cid, message)
                    ts.logout()
                    await ctx.send('\N{OK HAND SIGN}')
            else:
                await ctx.send('No user named %s' % user)
        else:
            await ctx.send('Please specify a username'.format(self.prefix))

    @ts.command(pass_context=True, usage='lastseen <user>')
    async def lastseen(self, ctx, user=None):
        """Shows the time since a user has been seen last"""
        if not user:
            return await ctx.send('Please specify a user')
        ts = TS3Server(self.config.ip, self.config.port, self.config.sid)
        ts.login(self.config.user, self.config.password)
        ts.set_client_nick('serveradmin')
        cldbids = ts.get_dbclids(user)
        if not cldbids:
            await ctx.send('No user with that name')
            return
        for cldbid in cldbids:
            await ctx.send(ts.lastseen(cldbid))
        ts.logout()

    async def afk_check(self):
        # TODO: Only enable when move_afk = True in config
        await self.bot.wait_until_ready()
        while True:
            ts = TS3Server(self.config.ip, self.config.port, self.config.sid)
            ts.login(self.config.user, self.config.password)
            ts.set_client_nick('serveradmin')
            ts.move_afk(self.config.afk_timeout, self.config.afk_channel_id)
            ts.logout()
            await asyncio.sleep(60)


def setup(bot):
    t = TS3(bot)
    bot.loop.create_task(t.afk_check())
    bot.add_cog(t)
