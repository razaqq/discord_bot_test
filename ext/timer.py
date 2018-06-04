from discord.ext import commands
import asyncio


class CountDown:
    def __init__(self, time, cog, msg, channel, author):
        self.time = time
        self.cog = cog
        self.msg = msg
        self.channel = channel
        self.author = author

    async def run(self):
        while self.time >= 0:
            await self.cog.update_timer(self, self.to_str(self.time))
            if self.time == 0:
                self.cog.timer_count -= 1
                break
            await asyncio.sleep(5)
            self.time -= 5

    def to_str(self, seconds):
        mins = int(seconds / 60)
        secs = seconds - mins * 60
        mins_str = ''
        secs_str = ''
        if len(str(mins)) == 1:
            mins_str += self.to_emoji(0)
        if len(str(secs)) == 1:
            secs_str += self.to_emoji(0)
        for digit in str(mins):
            mins_str += self.to_emoji(int(digit))
        for digit in str(secs):
            secs_str += self.to_emoji(int(digit))
        return '{}:{}'.format(mins_str, secs_str), seconds

    @staticmethod
    def to_emoji(number):
        unicode = {
            0: '\N{DIGIT ZERO}',
            1: '\N{DIGIT ONE}',
            2: '\N{DIGIT TWO}',
            3: '\N{DIGIT THREE}',
            4: '\N{DIGIT FOUR}',
            5: '\N{DIGIT FIVE}',
            6: '\N{DIGIT SIX}',
            7: '\N{DIGIT SEVEN}',
            8: '\N{DIGIT EIGHT}',
            9: '\N{DIGIT NINE}'
        }
        return unicode[number] + '\N{COMBINING ENCLOSING KEYCAP}'


class DiscordTimer:
    def __init__(self, bot):
        self.bot = bot
        self.timer_count = 0

    async def update_timer(self, timer, t):
        if not timer.msg:
            msg = await self.bot.send_message(timer.channel, t[0])
            timer.msg = msg
        else:
            await self.bot.edit_message(timer.msg, t[0])
            if t[1] == 0:
                await self.bot.edit_message(timer.msg, t[0] + timer.author.mention)

    def create_timer(self, seconds, channel, author):
        if self.timer_count < 3 and seconds <= 600:
            loop = asyncio.get_event_loop()
            t = CountDown(seconds, self, None, channel, author)
            loop.create_task(t.run())
            self.timer_count += 1
            return True
        return False

    @commands.command(pass_context=True)
    async def timer(self, ctx, seconds):
        if not self.create_timer(int(seconds), ctx.message.channel, ctx.message.author):
            await self.bot.say('10 Mins max and 3 timers at once only nerd')


def setup(bot):
    dt = DiscordTimer(bot)
    bot.add_cog(dt)




