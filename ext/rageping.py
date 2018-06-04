from discord.ext import commands


class RagePing:
    def __init__(self, bot):
        self.bot = bot
        self.prefix = self.bot.config['prefix']

    @commands.command(pass_context=True)
    async def rageping(self, ctx):
        """Repeats a ping five times"""
        msg = ctx.message
        role_mentions = msg.role_mentions
        user_mentions = msg.mentions

        if role_mentions or user_mentions:
            for role_mention in role_mentions:
                mention = role_mention.mention
                for i in range(5):
                    await self.bot.say(mention)

            for user_mention in user_mentions:
                mention = user_mention.mention
                for i in range(5):
                    await self.bot.say(mention)

        else:
            await self.bot.say('Usage: "{}rageping @ROLE"; You can mention one role/user '
                               'or a list of roles/users'.format(self.prefix))


def setup(bot):
    bot.add_cog(RagePing(bot))
