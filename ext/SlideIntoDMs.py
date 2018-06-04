from discord.ext import commands
import datetime
import json
import discord


class SlideIntoDMs:
    def __init__(self, bot):
        self.bot = bot
        self.prefix = self.bot.config['prefix']
        self.config = self.load_config(self.bot.workdir)

    @staticmethod
    def load_config(workdir):
        with open(workdir + '/config/SlideIntoDMs.json', 'r', encoding='utf-8') as doc:
            return json.load(doc)

    @commands.command(pass_context=True, hidden=True)
    async def dm(self, ctx, text=None):
        msg = ctx.message
        role_mentions = msg.role_mentions
        user_mentions = msg.mentions
        
        if msg.channel.is_private and msg.author != self.bot.user and text:
            await self.bot.say("Preparing your tweet...")
            # in private channel with msg.author
            all_servers = self.bot.servers
            server = discord.utils.get(all_servers, id=self.config['server_id'])
            channel = server.get_channel(self.config['channel_id'])
            await self.sendFakeNews(text, channel)
        else:
            await self.bot.say("Git gud")

    async def sendFakeNews(self, text, channel):
        now = datetime.datetime.now()
        embed = discord.Embed(description="{}\n\n[Link]({})".format(text, "http://perryswift.tk"), color=0x00aced)
        embed.set_author(name="Donald J. Trump", url='https://twitter.com/realDonaldTrump', icon_url="https://pbs.twimg.com/profile_images/874276197357596672/kUuht00m_normal.jpg")
        embed.set_footer(text=now.strftime("%Y-%m-%d"), icon_url='https://abs.twimg.com/icons/apple-touch-icon-192x192.png')
        embed.set_thumbnail(url='https://abs.twimg.com/icons/apple-touch-icon-192x192.png')

        await self.bot.send_message(channel, embed=embed)


def setup(bot):
    bot.add_cog(SlideIntoDMs(bot))
