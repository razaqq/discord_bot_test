from discord.ext import commands
from ts3py import server
import random
import asyncio


class Bomb(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prefix = self.bot.config.MAIN.prefix

    @commands.command(pass_context=True)
    @commands.guild_only()
    async def bomb(self, ctx):
        """Bombs a user"""
        user_mentions = ctx.message.mentions
        if len(user_mentions) == 1:
            wires = {0: '\N{LARGE BLUE CIRCLE}',
                     1: '\N{LARGE RED CIRCLE}',
                     2: '\N{MEDIUM BLACK CIRCLE}',
                     3: '\N{MEDIUM WHITE CIRCLE}'}
            answer = wires[random.randint(0, 3)]
            defuse_msg = await ctx.send(f'{user_mentions[0].mention} QUICK TRY TO DEFUSE THE \N{BOMB} '
                                        f'BY CHOOSING THE CORRECT WIRE, YOU HAVE 30 SECONDS!')
            for color in wires.values():
                await defuse_msg.add_reaction(color)

            def check(r, u):
                return u.id == user_mentions[0].id and r.message.id == defuse_msg.id

            try:
                choice = await self.bot.wait_for('reaction_add', check=check, timeout=30.0)

            except asyncio.TimeoutError:
                self.tskick(user_mentions[0])
                await ctx.send(f'KABOOOOM, you failed to make a choice! `{answer}` would have been correct!')
            else:
                if choice[0].emoji == answer:
                    await ctx.send('Puh you defused that just in time...')
                else:
                    self.tskick(user_mentions[0])
                    await ctx.send(f'KABOOOOM, you chose the wrong wire! `{answer}` would have been correct!')

        else:
            await ctx.send(f'Usage: `{self.prefix}bomb @User`')

    def tskick(self, user):
        if str(user) in self.bot.config.BOMB:
            to_kick = int(self.bot.config.BOMB[str(user)])
            ts = server.TS3Server(self.bot.config.TS3.ip, self.bot.config.TS3.port, self.bot.config.TS3.sid)
            ts.login(self.bot.config.TS3.user, self.bot.config.TS3.password)
            ts.set_client_nick('serveradmin')
            ts.clientkick(cldbid=to_kick, message='YOU EXPLODED!')


def setup(bot):
    bot.add_cog(Bomb(bot))
