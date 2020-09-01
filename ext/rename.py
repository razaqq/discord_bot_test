import re
import discord
import asyncio
from discord.ext import commands


class Rename(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.success = '\N{WHITE HEAVY CHECK MARK}'
        self.fail = '\N{CROSS MARK}'

    @commands.command(pass_context=True, no_pm=True)
    async def rename(self, ctx, *, msg):
        nick = re.sub(r'<.*?>\s', '', msg)
        if len(ctx.message.mentions) != 1:
            await ctx.send('You have to mention exactly one user.')
            return

        if not nick:
            await ctx.send("Username can't be empty.")
            return

        if len(nick) > 32:
            await ctx.send("Username can be 32 chars max.")
            return

        rename_user = ctx.message.mentions[0]

        react_msg = await ctx.send(f'This will rename `{rename_user.nick}` to `{nick}`. Are you sure?')
        await react_msg.add_reaction(self.success)
        await react_msg.add_reaction(self.fail)

        def check(reaction, user):
            return user.id == ctx.message.author.id and reaction.message.id == react_msg.id

        try:
            choice, _ = await self.bot.wait_for('reaction_add', check=check, timeout=30.0)
        except asyncio.TimeoutError:
            await ctx.send('Aborting...')
        else:
            if choice.emoji == self.success:
                try:
                    await rename_user.edit(nick=nick)
                    await ctx.send(':ok_hand:')
                except discord.Forbidden:
                    await ctx.send('I dont have permission for that.')
            elif choice.emoji == self.fail:
                await ctx.send('Aborting...')
            else:
                await ctx.send('Pls react with either of the two options given.')
            await react_msg.clear_reactions()


def setup(bot):
    r = Rename(bot)
    bot.add_cog(r)
