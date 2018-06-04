import discord
from discord.ext import commands
import logging


class Presence:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, enabled=False)
    async def game(self, ctx, *, game=None):
        server = ctx.message.server
        current_status = server.me.status if server is not None else None

        if game:
            game = game.strip()
            await self.bot.change_presence(game=discord.Game(name=game),
                                           status=current_status)
            logging.log(20, 'Status set to "{}" by owner'.format(game))
        else:
            await self.bot.change_presence(game=None, status=current_status)
            logging.log(20, 'status cleared by owner')
            await self.bot.say('\N{OK HAND SIGN}')

    @commands.command(pass_context=True, no_pm=True)
    async def rename(self, ctx, *, nickname=""):
        nickname = nickname.strip()
        if nickname == "":
            nickname = None
        try:
            await self.bot.change_nickname(ctx.message.server.me, nickname)
            await self.bot.say('\N{OK HAND SIGN}')
        except discord.Forbidden:
            await self.bot.say("I cannot do that, I lack the permission.")


def setup(bot):
    bot.add_cog(Presence(bot))
