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
            wires = {0: '🔴', 1: '🔵', 2: '⚪', 3: '⚫'}
            answer_num = random.randint(0, 3)
            answer = wires[answer_num]
            defuse_msg = await ctx.send('{} QUICK TRY TO DEFUSE THE 💣 BY CHOOSING THE RIGHT WIRE, YOU HAVE 30 SECONDS!'
                                        ''.format(user_mentions[0].mention))
            await defuse_msg.add_reaction('🔵')  # blue
            await defuse_msg.add_reaction('🔴')  # red
            await defuse_msg.add_reaction('⚫')  # black
            await defuse_msg.add_reaction('⚪')  # white

            def check(r, u):
                return u.id == user_mentions[0].id and r.message.id == defuse_msg.id

            try:
                choice = await self.bot.wait_for('reaction_add', check=check, timeout=30.0)

            except asyncio.TimeoutError:
                self.tskick(user_mentions[0])
                await ctx.send('KABOOOOM, you failed to make a choice! {} would have been correct!'.format(answer))
            else:
                # yield from bot.remove_reaction(defuse_msg, choice[0].emoji, choice[1])
                if choice[0].emoji == answer:
                    await ctx.send('Puh you defused that just in time...')
                else:
                    self.tskick(user_mentions[0])
                    await ctx.send('KABOOOOM, you chose the wrong wire! {} would have been correct!'.format(answer))

        else:
            await ctx.send('Usage: "{}bomb @USER"'.format(self.prefix))

    def tskick(self, user):
        if str(user) in self.bot.config.BOMB:
            to_kick = int(self.bot.config.BOMB[str(user)])
            ts = server.TS3Server(self.bot.config.TS3.ip, self.bot.config.TS3.port, self.bot.config.TS3.sid)
            ts.login(self.bot.config.TS3.user, self.bot.config.TS3.password)
            ts.set_client_nick('serveradmin')
            ts.clientkick(cldbid=to_kick, message='YOU EXPLODED!')


def setup(bot):
    bot.add_cog(Bomb(bot))
