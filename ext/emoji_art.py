from discord.ext import commands


class EmojiArt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def emojiart(self, ctx, text):
        if len(text) > 2:
            await ctx.send('Cannot do that, discords max char limit...')
        p = Picture(text, self.bot.root_dir)
        await ctx.send(p)


class Picture:
    def __init__(self, text, root_dir, spacer=''):
        self.letter_coords = self.load_config(root_dir)
        self.x = len(text) * 6 + 3
        self.y = 13
        self.spacer = spacer
        self.array = [['\U0001F192' for y in range(self.y)] for x in range(self.x)]
        self.add_border()
        self.print(text)

    def __str__(self):
        s = ''
        for y in range(self.y):
            for x in range(self.x):
                s += '{}{}'.format(self.array[x][y], self.spacer)
            s += '\n'
        return s

    def add_border(self):
        for y in range(self.y):
            for x in range(self.x):
                if y == 0 or x == 0 or y == self.y - 1 or x == self.x - 1:
                    self.array[x][y] = '\U0001F602'

    def print(self, text):
        i = 0
        for letter in text.upper():
            coords = self.letter_coords[letter]
            for x, y in coords:
                self.array[2 + (i * 6) + x][y + 2] = '\U0001F4AF'

            i += 1


def setup(bot):
    e = EmojiArt(bot)
    bot.add_cog(e)


if __name__ == '__main__':
    e = Picture('pro', '.', ' ')
    print(e)


