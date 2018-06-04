from discord.ext import commands
from ts3_mod import server
import json
import random


class Bomb:
    def __init__(self, bot):
        self.bot = bot
        self.config = self.bot.config
        self.userdb = self.load_config()
        self.prefix = self.bot.config['prefix']

    def load_config(self):
        with open(self.bot.workdir + '/config/bomb.json', 'r', encoding='utf-8') as doc:
            return json.load(doc)

    @commands.command(pass_context=True)
    async def bomb(self, ctx):
        """Bombs a user"""
        user_mentions = ctx.message.mentions
        if len(user_mentions) == 1:
            wires = {0: '🔴', 1: '🔵', 2: '⚪', 3: '⚫'}
            answer_num = random.randint(0, 3)
            answer = wires[answer_num]
            defuse_msg = await self.bot.say(
                '{} QUICK TRY TO DEFUSE THE 💣 BY CHOOSING THE RIGHT WIRE, YOU HAVE 30 SECONDS!'.format(
                    user_mentions[0].mention))
            await self.bot.add_reaction(defuse_msg, '🔵')  # blue
            await self.bot.add_reaction(defuse_msg, '🔴')  # red
            await self.bot.add_reaction(defuse_msg, '⚫')  # black
            await self.bot.add_reaction(defuse_msg, '⚪')  # white
            choice = await self.bot.wait_for_reaction(emoji=None, user=user_mentions[0], timeout=30, message=defuse_msg)
            if choice is None:
                self.tskick(user_mentions[0])
                await self.bot.say('KABOOOOM, you failed to make a choice! {} would have been correct!'.format(answer))
            else:
                # yield from bot.remove_reaction(defuse_msg, choice[0].emoji, choice[1])
                if choice[0].emoji == answer:
                    await self.bot.say('Puh you defused that just in time...')
                else:
                    self.tskick(user_mentions[0])
                    await self.bot.say('KABOOOOM, you chose the wrong wire! {} would have been correct!'.format(answer))

        else:
            await self.bot.say('Usage: "{}bomb @USER"'.format(self.prefix))

    def tskick(self, user):
        if str(user) in self.userdb:
            to_kick = int(self.userdb[str(user)])
            ts = server.TS3Server(self.config['ts3ip'], self.config['ts3port'], self.config['ts3sid'])
            ts.login(self.config['ts3user'], self.config['ts3pass'])
            ts.set_client_nick('serveradmin')
            ts.clientkick(cldbid=to_kick, message='YOU EXPLODED!')


def setup(bot):
    bot.add_cog(Bomb(bot))
