from discord.ext import commands


class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def test(self, ctx):
        if ctx.invoked_subcommand is None:
            guild = self.bot.get_guild(self.config.guild_id)
            channel = guild.get_channel(self.config.channel_id)

    @test.command(pass_context=True, usage='idk', parent='test')
    async def newtest(self, ctx, text):
        await ctx.send(text)


def setup(bot):
    bot.add_cog(Test(bot))
