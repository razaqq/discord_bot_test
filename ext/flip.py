from discord.ext import commands


class Flip(commands.Cog):
    def __init__(self, bot):
        self.prefix = bot.config.MAIN.prefix

    @commands.command()
    async def flip(self, ctx, *, string=None):
        """Makes you feel like an australian"""
        if string:
            string = string.lower()
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

            await ctx.send(end_string)
            await ctx.send('*Do you feel like an australian yet?*')
        else:
            await ctx.send('Usage: {}flip <your text here>'.format(self.prefix))


def setup(bot):
    bot.add_cog(Flip(bot))
