from discord.ext import commands
import asyncio
from unicodedata import lookup


class React(commands.Cog):
    @commands.command()
    @commands.guild_only()
    async def react(self, ctx, *, msg):
        """Reacts to the message above with text. 1 letter once only"""
        if msg:
            if len(msg) > 15:
                await ctx.send('Your text is too long, 15 chars max')
                return
            msg = msg.upper()
            await ctx.message.delete()
            last_msg = (await ctx.channel.history(limit=1).flatten())[0]

            a = self.check_reactable(msg)
            if not a:
                await ctx.send('I can only react with text that contains a char once')
                return
            for char in a:
                await last_msg.add_reaction(lookup('Regional Indicator Symbol Letter {0}'.format(char)))
                await asyncio.sleep(1)

    @staticmethod
    def check_reactable(msg):
        used = []
        for char in msg:
            if char not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                continue
            if char not in used:
                used.append(char)
            else:
                return False
        return used


def setup(bot):
    r = React()
    bot.add_cog(r)
