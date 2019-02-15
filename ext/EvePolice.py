import json
import logging


class EvePolice:
    def __init__(self, bot):
        self.bot = bot
        self.prefix = self.bot.config['prefix']
        # self.bot.on_message = self.on_message
        # self.bot.on_message = self.on_message
        # self.config = self.load_config(self.bot.root_dir)

    @staticmethod
    def load_config(root_dir):
        with open(root_dir + '/config/SlideIntoDMs.json', 'r', encoding='utf-8') as doc:
            return json.load(doc)

    def inspect(self, content):
        lower_content = str(content).lower()
        if "zkill" in lower_content:
            return True

        words = lower_content.split(" ")
        banned_words = ["fozzie", "machariel", "entosis", "ragnarok", "ahac", "ahacs", "blops", "aeon", "zkill", "hedliner", "dancul", "kb", "killboard", "ratting", "nyx", "querious", "insmother", "jita", "lazerhawk", "isk", "lazerhawks", "lzhx", "goons", "incursion", "fc", "cfc", "c3", "c4", "c5", "fortizar", "astrahus"]
        suspicious_words = ["rent", "bil", "renting", "unrented", "pandemic", "horde", "legion", "fort",
                            "astra", "wh", "site", "sites", "dread", "fleet", "hole", "wormhole", "wormholes","alliance",
                            "deployment", "eve", "dropped","hotdropped", "drop", "hotdrop", "gating", "roaming", "roam", "gate", "delve", "rent", "hawks"]
        count = 0
        for word in words:
            if word in banned_words:
                return True
            elif word in suspicious_words:
                count = count + 1
                if count >= 2:
                    return True
        return False

    async def police(self, message):
        logging.info("\n[POLICE] \n------\n%s\n------\n" % message.content)
        await self.bot.delete_message(message)
        return "This in an eve-safe channel."

    async def on_message(self, message):
        """
        This event triggers on every message received by the bot. Including one's that it sent itself.
        """
        if message.author.bot:
            return

        if self.inspect(message.content):
            result = await self.police(message)
            await self.bot.send_message(message.channel, result)


def setup(bot):
    bot.add_cog(EvePolice(bot))
