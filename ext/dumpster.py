from discord.ext import commands
from ts3py import server
import json


class Dumpster:
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
                        await self.bot.say('\N{OK HAND SIGN}')
                    else:
                        await self.bot.say('He is already there...')

            else:
                await self.bot.say('No user named {}'.format(name))
        else:
            await self.bot.say('Usage: {}dumpster <user>'.format(self.bot.config['prefix']))


def setup(bot):
    bot.add_cog(Dumpster(bot))
