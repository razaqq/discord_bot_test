import logging
from discord.ext import commands


class EvePolice(commands.Cog):
    def __init__(self, bot):
        self.config = bot.config.EVE_POLICE
        self.banned_words = self.config.banned_words.split(',')
        self.suspicious_words = self.config.suspicious_words.split(',')

    def inspect(self, content):
        words = str(content).lower().split(" ")
        count = 0
        for word in words:
            if word in self.banned_words:
                return True
            elif word in self.suspicious_words:
                count = count + 1
                if count >= 2:
                    return True
        return False

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if self.inspect(message.content):
            logging.info("Deleting message: {}".format(message.content))
            await message.delete()
            await message.channel.send("This in an eve-safe channel.")


def setup(bot):
    bot.add_cog(EvePolice(bot))
