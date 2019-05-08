import os
from discord.ext import commands
import fnmatch
import re


class Source(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def source(self, ctx, file=None):
        """Shows source code of a filename"""
        if not file:
            return await ctx.send('https://github.com/razaqq/discord_bot')
        for chunks in self.get_source(file):
            await ctx.send(chunks)

    def get_source(self, file):
        includes = ['*{}.py'.format(file)]  # for files only
        excludes = ['*venv*', '*pubg_mod*', '*__init__.py', '*.git*', '*config*']
        includes = r'|'.join([fnmatch.translate(x) for x in includes])
        excludes = r'|'.join([fnmatch.translate(x) for x in excludes]) or r'$.'

        for root, dirs, files in os.walk(self.bot.root_dir):
            # exclude dirs
            dirs[:] = [os.path.join(root, d) for d in dirs]
            dirs[:] = [d for d in dirs if not re.match(excludes, d)]

            # exclude/include files
            files = [os.path.join(root, f) for f in files]
            files = [f for f in files if not re.match(excludes, f)]
            files = [f for f in files if re.match(includes, f)]

            if len(files) == 1:
                with open(files[0], 'r') as f:
                    s = f.read()
                    chunks = []
                    for start in range(0, len(s), 1900):
                        text = s[start:start+1900].replace('`', '"')
                        chunks.append('```py\n{}```'.format(text))
                    return chunks
            if len(files) > 1:
                return ['There is multiple files with that name.']

        return ['No file with that name found.']


def setup(bot):
    s = Source(bot)
    bot.add_cog(s)


if __name__ == '__main__':
    class Bot:
        def __init__(self):
            self.root_dir = os.path.dirname(os.path.abspath(__file__ + '/..'))
    b = Bot()

    s = Source(b)
    print(s.get_source('bot'))
