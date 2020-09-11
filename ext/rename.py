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

        author = ctx.message.author
        rename_user = ctx.message.mentions[0]

        if rename_user.id == self.bot.user.id:
            await ctx.send('Good try.')
            return

        if rename_user.id == author.id:
            await ctx.send('You cannot rename yourself.')
            return

        if not nick:
            await ctx.send('Username cannot be empty.')
            return

        if len(nick) > 32:
            await ctx.send('Username can be 32 chars max.')
            return

        react_msg = await ctx.send(f'This will rename `{rename_user.nick}` to `{nick}`. Are you sure?')
        await react_msg.add_reaction(self.success)
        await react_msg.add_reaction(self.fail)

        def check(reaction, user):
            return user.id == author.id and reaction.message.id == react_msg.id

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
                await ctx.send('Time ran out, aborting...')
            else:
                await ctx.send('Pls react with either of the two options given.')
            await react_msg.clear_reactions()

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if str(before.guild.id) != self.bot.config.MAIN.main_guild:
            return

        if before.bot or after.bot:
            return

        source = None
        async for entry in before.guild.audit_logs(action=discord.AuditLogAction.member_update, limit=3):
            if entry.before.nick == before.nick and entry.after.nick == after.nick and entry.target.id == before.id:
                source = entry.user
                break

        if not source or source.bot or source.id != before.id:
            return

        if before.nick != after.nick:
            try:
                await after.edit(nick=before.nick)
            except discord.Forbidden:
                pass


def setup(bot):
    r = Rename(bot)
    bot.add_cog(r)
