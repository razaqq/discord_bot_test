from discord.ext import commands


class Flip:
    def __init__(self, bot):
        self.bot = bot
        self.config = self.bot.config

    @commands.command()
    async def flip(self, *, string=None):
        """Makes you feel like an australian"""
        if string:
            chars = "abcdefghijklmnopqrstuvwxyz"
            tran = "ɐqɔpǝɟƃɥᴉɾʞlɯuodbɹsʇnʌʍxʎz"
            end_string = ''

            string = string[::-1]

            for c in string:
                if c in chars:
                    index = chars.index(c)
                    new_c = tran[index]
                    end_string += new_c
                elif c == '\t':
                    end_string += '\t'
                else:
                    end_string += c

            await self.bot.say(end_string)
            await self.bot.say('*Do you feel like an australian yet?*')
        else:
            await self.bot.say('Usage: {}flip <your text here>'.format(self.config['prefix']))



def setup(bot):
    bot.add_cog(Flip(bot))
