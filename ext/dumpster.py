from discord.ext import commands
from ts3py import server


class Dumpster(commands.Cog):
    def __init__(self, bot):
        self.config = bot.config.TS3
        self.prefix = bot.config.MAIN.prefix

    @commands.command(pass_context=True)
    async def dumpster(self, ctx, *, name=None):
        if name:
            author = ctx.message.author.name

            ts = server.TS3Server(self.config.ip, self.config.port, self.config.sid)
            ts.login(self.config.user, self.config.password)
            ts.set_client_nick('The Dumpsterer')

            cids = ts.get_clids(name)

            if cids is not None:
                for cid in cids:
                    res1 = ts.clientmove(cid, str(13))
                    if res1:
                        ts.clientpoke(cid, 'You just got dumpstered by {}'.format(author))
                        ts.logout()
                        await ctx.send('\N{OK HAND SIGN}')
                    else:
                        await ctx.send('He is already there...')

            else:
                await ctx.send('No user named {}'.format(name))
        else:
            await ctx.send('Usage: {}dumpster <user>'.format(self.prefix))


def setup(bot):
    bot.add_cog(Dumpster(bot))
