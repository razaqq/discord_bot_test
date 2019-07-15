from discord.ext import tasks, commands
import time
import sqlite3
from prettytable import PrettyTable
import datetime
from math import ceil
import os
import logging


class RemindMe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.prefix = bot.config.MAIN.prefix
        self.units = {'minute': 60,
                      'hour': 60*60,
                      'day': 60*60*24,
                      'week': 60*60*24*7,
                      'month': 60*60*24*7*30}

        self.conn, self.cursor = self.get_db_connection()
        self.saved_reminders = []
        self.read_reminders()
        self.check_reminders.start()

    def get_db_connection(self):
        existing = os.path.isfile(os.path.join(self.bot.root_dir, 'databases/remindme.db'))
        conn = sqlite3.connect(os.path.join(self.bot.root_dir, 'databases/remindme.db'))
        cursor = conn.cursor()
        if not existing:
            logging.info('DB not found, creating empty tables...')
            cursor.execute('CREATE TABLE IF NOT EXISTS reminders ('
                           'USER INTEGER, SERVER INTEGER, CHANNEL INTEGER, FINISHES INTEGER, MESSAGE TEXT'
                           ')'
                           )
            conn.commit()
        return conn, cursor

    def read_reminders(self):
        _code = 'SELECT * FROM reminders;'
        self.cursor.execute(_code)
        _res = self.cursor.fetchall()
        reminders = []
        for res in _res:
            reminder = dict()
            reminder['USER'] = res[0]
            reminder['SERVER'] = res[1]
            reminder['CHANNEL'] = res[2]
            reminder['FINISHES'] = int(res[3])
            reminder['MESSAGE'] = res[4]
            reminders.append(reminder)
        self.saved_reminders = reminders

    def add_reminder(self, user, server, channel, finishes, text):
        try:
            _code = 'INSERT INTO reminders VALUES ("{}", "{}", "{}", {}, "{}")'.format(user, server, channel, finishes, text)
            self.cursor.execute(_code)
            self.conn.commit()
            self.read_reminders()
            return True
        except Exception:
            return False

    def remove_all_reminders(self, user):
        _code = 'DELETE FROM reminders WHERE USER="{}";'.format(user)
        self.cursor.execute(_code)
        self.conn.commit()
        self.read_reminders()

    def remove_reminder(self, user, finishes, text):
        _code = 'DELETE FROM reminders WHERE USER="{}" AND FINISHES={} AND MESSAGE="{}";'.format(user, finishes, text)
        self.cursor.execute(_code)
        self.conn.commit()
        self.read_reminders()

    def get_reminders(self, user):
        return [(r['FINISHES'], r['MESSAGE']) for r in self.saved_reminders if r['USER'] == user]

    @commands.command(pass_context=True, no_pm=True)
    @commands.guild_only()
    async def remindme(self, ctx, quantity: int = 0, time_unit: str = None, *, text: str = None):
        """Reminds you in a specified time with a specified text"""
        time_unit = time_unit.lower()
        if (quantity > 0) and text and (time_unit in self.units):
            time_unit = time_unit.lower()
            s = ''
            if time_unit.endswith("s"):
                time_unit = time_unit[:-1]
                s = 's'

            user = ctx.message.author.id
            guild = ctx.message.guild.id
            channel = ctx.message.channel.id
            seconds = quantity * self.units[time_unit]
            finishes = int(time.time() + seconds)
            self.add_reminder(user, guild, channel, finishes, text)
            await ctx.send('Will remind you in {} {}{}: "{}"'.format(str(quantity), time_unit, s, text))
        else:
            await ctx.send('Usage: {}remindme <amount> <unit> <message>'.format(self.prefix))

    @commands.command(pass_context=True, no_pm=True)
    @commands.guild_only()
    async def forgetme(self, ctx):
        """Forgets all your reminders"""
        user = ctx.message.author.id
        self.remove_all_reminders(user)
        await ctx.send('\N{OK HAND SIGN}')

    @commands.command(pass_context=True, no_pm=True)
    @commands.guild_only()
    async def reminders(self, ctx):
        """Shows all your reminders"""
        user = ctx.message.author.id
        res = self.get_reminders(user)
        if not res:
            await ctx.send('No reminders saved for you!')
            return

        t = PrettyTable()
        t.left_padding_width = 1
        t.right_padding_width = 1
        t.title = 'Your reminders'
        t.field_names = ['Time left', 'Msg']
        t.align['Time left'] = 'r'
        t.align['Msg'] = 'l'

        for r in res:
            time_str = '{:0>8}'.format(str(datetime.timedelta(seconds=r[0] - int(time.time()))))
            text_rows = ceil(len(r[1]) / 80)
            row = [time_str, r[1][:80]]
            t.add_row(row)
            for i in range(1, text_rows):
                row = ['', r[1][80*i:80*(i+1)]]
                t.add_row(row)

        await ctx.send('```{}```'.format(t.get_string()))

    @tasks.loop(seconds=10)
    async def check_reminders(self):
        for reminder in self.saved_reminders:
            if reminder['FINISHES'] <= int(time.time()):
                guild = self.bot.get_guild(reminder['SERVER'])
                channel = guild.get_channel(reminder['CHANNEL'])
                user = self.bot.get_user(id=reminder['USER'])
                await channel.send('{} Here is your reminder: "{}"'.format(user.mention, reminder["MESSAGE"]))
                self.remove_reminder(reminder['USER'], reminder['FINISHES'], reminder['MESSAGE'])

    def cog_unload(self):
        self.check_reminders.cancel()


def setup(bot):
    r = RemindMe(bot)
    # loop = asyncio.get_event_loop()
    # loop.create_task(r.check_reminders())
    bot.add_cog(r)


if __name__ == '__main__':
    class Bot:
        def __init__(self):
            self.config = lambda: None
            self.root_dir = '.'
            setattr(self.config, 'MAIN', lambda: None)
            setattr(self.config.MAIN, 'prefix', 'abc')

    bot = Bot()
    r = RemindMe(bot)
    r.get_reminders(104901117158121472)
