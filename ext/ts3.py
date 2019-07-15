from discord.ext import tasks, commands
from ts3py.server import TS3Server


class TS3(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config.TS3
        self.prefix = bot.config.MAIN.prefix
        self.afk_check.start()

    def connect(self, username='serveradmin'):
        ts = TS3Server(self.config.ip, self.config.port, self.config.sid)
        ts.login(self.config.user, self.config.password)
        ts.set_client_nick(username)
        return ts

    @commands.group(pass_context=True)
    async def ts(self, ctx):
        """Shows a channeltree"""
        if ctx.invoked_subcommand is None:
            ts = self.connect()
            tree = ts.get_channeltree()
            ts.logout()
            if not tree:
                return await ctx.send('nobody is here <:feelsbad:345232499103891456>')
            await ctx.send('```{}```'.format(tree))

    @ts.command(pass_context=True, usage='poke <user>')
    async def poke(self, ctx, user=None, message=''):
        """Pokes a user with !ts poke "<username>" "Message here" """
        author = ctx.author.name
        if not user:
            return await ctx.send('Please specify a username'.format(self.prefix))

        ts = self.connect(author + ' via Discord')
        cids = ts.get_clids(user)
        if cids:
            for cid in cids:
                ts.clientpoke(cid, message)
            await ctx.send('\N{OK HAND SIGN}')
        else:
            await ctx.send('No user named {}'.format(user))
        ts.logout()

    @ts.command(pass_context=True, usage='lastseen <user>')
    async def lastseen(self, ctx, user=None):
        """Shows the time since a user has been seen last"""
        if not user:
            return await ctx.send('Please specify a user')
        ts = self.connect()
        cldbids = ts.get_dbclids(user)
        ts.logout()
        if not cldbids:
            await ctx.send('No user with that name')
        else:
            for cldbid in cldbids:
                await ctx.send(ts.lastseen(cldbid))

    @tasks.loop(seconds=60)
    async def afk_check(self):
        # TODO: Only enable when move_afk = True in config
        ts = self.connect()
        ts.move_afk(self.config.afk_timeout, self.config.afk_channel_id)
        ts.logout()

    def cog_unload(self):
        self.afk_check.cancel()


def setup(bot):
    t = TS3(bot)
    bot.add_cog(t)
