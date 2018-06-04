import discord
from discord.ext import commands
import random


class EightBall:
    def __init__(self, bot):
        self.bot = bot
        self.prefix = bot.config['prefix']

    @commands.command(pass_context=True)
    async def eightball(self, ctx, *, question=None):
        """Doesnt lie. EVER"""
        if question:
            author = ctx.message.author
            answer_list = ["It is certain",
                           "It is decidedly so",
                           "Without a doubt",
                           "Yes, definitely",
                           "You may rely on it",
                           "As I see it, yes",
                           "Most likely",
                           "Outlook good",
                           "Yes",
                           "Signs point to yes",
                           "Reply hazy try again",
                           "Ask again later",
                           "Better not tell you now",
                           "Cannot predict now",
                           "Concentrate and ask again",
                           "Don't count on it",
                           "My reply is no",
                           "My sources say no",
                           "Outlook not so good",
                           "Very doubtful",
                           "You are gay pwnd"]
            answer = random.choice(answer_list)
            await self.bot.say('{}: {}'.format(author.mention, answer))
        else:
            await self.bot.say('Usage: {}eightball <question>'.format(self.prefix))


def setup(bot):
    bot.add_cog(EightBall(bot))
