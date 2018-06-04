import discord
from discord.ext import commands
import time
import sqlite3
import asyncio


class RemindMe:
    def __init__(self, bot):
        self.bot = bot
        self.prefix = bot.config['prefix']
        self.units = {'minute': 60,
                      'hour': 60*60,
                      'day': 60*60*24,
                      'week': 60*60*24*7,
                      'month': 60*60*24*7*30}

        self.conn = sqlite3.connect(self.bot.workdir + '/databases/remindme.db')
        self.cursor = self.conn.cursor()
        self.reminders = []
        self.read_reminders()

    def read_reminders(self):
        read_untill = time.time() + (60*60*25)  # read reminders of next 25h
        _code = 'SELECT * FROM reminders WHERE FINISHES<{};'.format(read_untill)
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
        self.reminders = reminders

    def add_reminder(self, user, server, channel, finishes, text):
        try:
            _code = 'INSERT INTO reminders VALUES ("{}", "{}", "{}", {}, "{}")'.format(user, server, channel, finishes, text)
            self.cursor.execute(_code)
            self.conn.commit()
            if finishes < (time.time() + 60*60*25):  # only read reminders, if added one finishes in next 25h
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

    @commands.command(pass_context=True, no_pm=True)
    async def remindme(self, ctx, quantity: int=0, time_unit: str=None, *, text: str=None):
        if time_unit:
            time_unit = time_unit.lower()
            if time_unit.endswith("s"):
                time_unit = time_unit[:-1]
                s = 's'
            else:
                s = ''

        if (quantity > 0) and text and (time_unit in self.units):
            user = ctx.message.author.id
            server = ctx.message.server.id
            channel = ctx.message.channel.id
            seconds = quantity * self.units[time_unit]
            finishes = int(time.time() + seconds)
            self.add_reminder(user, server, channel, finishes, text)
            await self.bot.say('Will remind you in {} {}{}: "{}"'.format(str(quantity), time_unit, s, text))
        else:
            await self.bot.say('Usage: {}remindme <amount> <unit> <message>'.format(self.prefix))

    @commands.command(pass_context=True, no_pm=True)
    async def forgetme(self, ctx):
        user = ctx.message.author.id
        self.remove_all_reminders(user)
        await self.bot.say('\N{OK HAND SIGN}')

    async def check_reminders(self):
        while self is self.bot.get_cog('RemindMe'):
            for reminder in self.reminders:
                if reminder['FINISHES'] <= int(time.time()):
                    all_servers = self.bot.servers
                    server = discord.utils.get(all_servers, id=str(reminder['SERVER']))
                    channel = server.get_channel(str(reminder['CHANNEL']))
                    user = discord.User(id=reminder['USER'])
                    await self.bot.send_message(channel, '{} Here is your reminder: "{}"'.format(user.mention, reminder["MESSAGE"]))
                    self.remove_reminder(reminder['USER'], reminder['FINISHES'], reminder['MESSAGE'])
            await asyncio.sleep(10)


def setup(bot):
    r = RemindMe(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(r.check_reminders())
    bot.add_cog(r)
