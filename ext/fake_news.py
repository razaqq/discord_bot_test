from discord.ext import commands
import datetime
import discord


class FakeNews(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prefix = self.bot.config.MAIN.prefix
        self.config = self.bot.config.FAKE_NEWS

    @commands.command(pass_context=True, hidden=True)
    async def fake(self, ctx, *, text=None):
        msg = ctx.message
        if msg.guild is None and msg.author != self.bot.user and text:
            await ctx.send("Preparing your tweet...")
            # in private channel with msg.author
            # all_guilds = self.bot.guilds
            # guild = discord.utils.get(all_guilds, id=self.config['server_id'])
            print(type(self.config.guild_id))
            guild = self.bot.get_guild(id=int(self.config.guild_id))
            channel = guild.get_channel(channel_id=int(self.config.channel_id))
            await self.send_fake_news(text, channel)
        else:
            await ctx.send("Git gud")

    @staticmethod
    async def send_fake_news(text, channel):
        now = datetime.datetime.now()
        now = now.strftime("%a %b %d %H:%M:%S +0000 %Y")
        embed = discord.Embed(description="{}\n\n[Link]({})".format(text, "http://www.perry-swift.de"), color=0x00aced)
        embed.set_author(name="Donald J. Trump", url='https://twitter.com/realDonaldTrump',
                         icon_url="https://pbs.twimg.com/profile_images/874276197357596672/kUuht00m_normal.jpg")
        embed.set_footer(text=now,
                         icon_url='https://abs.twimg.com/icons/apple-touch-icon-192x192.png')
        embed.set_thumbnail(url='https://abs.twimg.com/icons/apple-touch-icon-192x192.png')

        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(FakeNews(bot))
