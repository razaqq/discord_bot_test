from discord.ext import commands
from ts3py import server
import json


class Dumpster(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.load_config(self.bot.root_dir)

    @staticmethod
    def load_config(root_dir):
        with open(root_dir + '/config/ts3.json', 'r', encoding='utf-8') as doc:
            return json.load(doc)

    @commands.command(pass_context=True)
    async def dumpster(self, ctx, *, name=None):
        if name:
            author = ctx.message.author.name

            ts = server.TS3Server(self.config['ts3ip'], self.config['ts3port'], self.config['ts3sid'])
            ts.login(self.config['ts3user'], self.config['ts3pass'])
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
            await ctx.send('Usage: {}dumpster <user>'.format(self.bot.config['prefix']))


def setup(bot):
    bot.add_cog(Dumpster(bot))
