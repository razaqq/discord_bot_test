import json
import logging
from discord.ext import  commands


class EvePolice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prefix = self.bot.config['prefix']
        self.config = self.load_config(self.bot.root_dir)
        self.banned_words = self.config['banned_words']
        self.suspicious_words = self.config['suspicious_words']

    @staticmethod
    def load_config(root_dir):
        with open(root_dir + '/config/eve_police.json', 'r', encoding='utf-8') as doc:
            return json.load(doc)

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

    async def on_message(self, message):
        """
        This event triggers on every message received by the bot. Including one's that it sent itself.
        """
        if message.author.bot:
            return

        if self.inspect(message.content):
            logging.info("Deleting message: {}".format(message.content))
            await message.delete()
            await message.channel.send("This in an eve-safe channel.")


def setup(bot):
    bot.add_cog(EvePolice(bot))
