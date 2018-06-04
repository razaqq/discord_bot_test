from discord.ext import commands
from ts3_mod import server


class TS3:
    def __init__(self, bot):
        self.bot = bot
        self.config = self.bot.config
        self.prefix = self.config['prefix']

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
        """!ts poke "<username>" "Message here" """
        author = ctx.message.author.name
        if not message:
            message = ''
        if user:
            ts = server.TS3Server(self.config['ts3ip'], self.config['ts3port'], self.config['ts3sid'])
            ts.login(self.config['ts3user'], self.config['ts3pass'])
            ts.set_client_nick(author + ' via Discord')
            cids = ts.get_cids(user)
            if cids is not None:
                for cid in cids:
                    ts.clientpoke(cid, message)
                    ts.logout()
                    await self.bot.say('\N{OK HAND SIGN}')
            else:
                await self.bot.say('No user named %s' % user)
        else:
            await self.bot.say('Usage: {}ts poke "<username>" "Message here"'.format(self.prefix))


def setup(bot):
    bot.add_cog(TS3(bot))
