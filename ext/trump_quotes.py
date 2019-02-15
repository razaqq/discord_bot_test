import time
import operator
from prettytable import PrettyTable
import sqlite3
from distutils import util
import logging
from discord.ext import commands
from datetime import datetime


class TrumpQuote:
    def __init__(self, root_dir):
        # sqlite
        self.conn = sqlite3.connect('{}/databases/trump_quotes.db'.format(root_dir))
        self.cursor = self.conn.cursor()

        self.text = None
        self.answer = None
        self.get_quote()
        self.up_votes = 0
        self.down_votes = 0
        self.total_votes = 0
        self.msg = None
        self.start_time = time.time()
        self.stats = Stats(root_dir)
        self.votes = {}

    def get_quote(self):
        _code = 'SELECT * FROM quotes ORDER BY RANDOM() LIMIT 1;'
        self.cursor.execute(_code)
        _res = self.cursor.fetchall()[0]
        _quote = _res[0]
        _answer = util.strtobool(_res[1])
        _text = (
                '*"' + _quote + '"*' + '\n' + '\n' + '- Donald John Trump, President of the United States of America'
                + '\n' + '\n' + '---------------------------------------------------------------'
                + '\n' + '\n' + 'You think this is a real quote? Vote below, answer in 1 min'
        )
        self.text = _text
        self.answer = _answer

    def get_result(self):
        if self.answer:
            _answer = 'REAL'
        else:
            _answer = 'FAKE'
        self.text += (
                '\n' + '\n' + '---------------------------------------------------------------'
                + '\n' + '{} people think that this is a real quote and {} think its fake'.format(self.up_votes, self.down_votes)
                + '\n' + '---------------------------------------------------------------'
                + '\n' + 'The quote was {}.'.format(_answer)
        )
        return self.text

    def add_quote(self, quote, answer):
        _code = 'INSERT INTO quotes VALUES ("{}", "{}")'.format(quote, answer)
        self.cursor.execute(_code)
        self.conn.commit()

    def add_vote(self, user, emoji):
        user = user.lower()
        if user in self.votes:
            return
        if emoji == '👍':
            self.up_votes += 1
            if self.answer:
                self._add_points(user, 10)
                self.votes[user] = True
            elif not self.answer:
                self._add_points(user, -5)
                self.votes[user] = False

        elif emoji == '👎':
            self.down_votes += 1
            if not self.answer:
                self._add_points(user, 10)
                self.votes[user] = True
            elif self.answer:
                self._add_points(user, -5)
                self.votes[user] = False

    def _add_points(self, player, amount):
        before = self.stats.stats[player]
        self.stats._set_points(player, before + amount)


class Stats:
    def __init__(self, root_dir):
        # sqlite
        self.conn = sqlite3.connect('{}/databases/trump_quotes.db'.format(root_dir))
        self.cursor = self.conn.cursor()

        self.stats = {}
        self._read()

    def add_points(self, player, points):
        if self._exists(player):
            _new = self.stats[player] + points
            self._set_points(player, _new)
            self.stats[player.lower()] += points
        else:
            code = 'INSERT INTO stats VALUES ("{}", {})'.format(player, points)
            self.cursor.execute(code)
            self.conn.commit()
            self.stats[player.lower()] = points

    def _set_points(self, player, points):
        code = 'UPDATE stats SET points = {} WHERE player = "{}";'.format(points, player)
        self.cursor.execute(code)
        self.conn.commit()

    def _exists(self, player):
        code = 'SELECT EXISTS(SELECT 1 FROM stats WHERE player="{}" LIMIT 1);'.format(player)
        self.cursor.execute(code)
        _res = self.cursor.fetchall()[0][0]
        return _res

    def _read(self):
        code = 'SELECT * FROM stats'
        self.cursor.execute(code)
        _res = self.cursor.fetchall()
        for player, points in _res:
            self.stats[player] = points

    def _sort(self):
        sort = dict(sorted(self.stats.items(), key=operator.itemgetter(1), reverse=True))
        return sort

    def get_table(self):
        t = PrettyTable()
        t.left_padding_width = 1
        t.right_padding_width = 1
        t.title = 'Trump Supporters'
        t.field_names = ['Rank', 'Player', 'Points']
        t.align['Rank'] = "r"
        t.align['Points'] = "r"
        t.align['Player'] = 'l'
        rank = 1
        for player, points in self._sort().items():
            row = [rank, player, points]
            t.add_row(row)
            rank += 1
        return t


class DiscordTrumpQuote:
    def __init__(self, bot):
        self.bot = bot
        self.last_quote = None
        self.prefix = self.bot.config['prefix']

    @commands.group(pass_context=True)
    async def trump(self, ctx):
        """Vote with the Buttons, use the refresh button after 1 min to get answer"""
        if ctx.invoked_subcommand is None:
            if self.last_quote is not None:  # does a quote exist?
                await self.bot.delete_message(self.last_quote)  # remove old quote
            q = TrumpQuote(self.bot.root_dir)
            self.last_quote = await self.bot.say(q.text)

            await self.bot.add_reaction(self.last_quote, '👍')
            await self.bot.add_reaction(self.last_quote, '👎')
            await self.bot.add_reaction(self.last_quote, '🔄')

            while True:  # rework this
                if (time.time() - q.start_time) > 60:
                    break

                res = await self.bot.wait_for_reaction(['👍', '👎', '🔄'], message=self.last_quote)
                if res.user.id != self.bot.user.id:
                    q.add_vote(res.user.name, res.reaction.emoji)
                    await self.bot.remove_reaction(self.last_quote, res.reaction.emoji, res.user)

            await self.bot.edit_message(self.last_quote, q.get_result())
            del q

    @trump.command()
    async def stats(self):
        """Shows stats"""
        s = Stats(self.bot.root_dir)
        table = s.get_table()
        await self.bot.say('```' + str(table) + '```')
        del s

    @trump.command(pass_context=True)
    async def add(self, ctx, quote=None, answer=None):
        """Adds a quote, usage: !trump add "This is a new quote" "False" """
        author = ctx.message.author
        msg = ctx.message
        if (quote is not None) and (answer is not None) and (answer in ['True', 'False']):
            _q = TrumpQuote(self.bot.root_dir)
            _q.add_quote(quote, answer)
            logging.log(20, '{}: {} added the quote "{}" with answer {}'.format(datetime.now(), author, quote, answer))
            await self.bot.delete_message(msg)
            await self.bot.say('Added your quote successfully! Use {}trump add <"quote"> <"True/False">'.format(self.prefix))
        else:
            await self.bot.say('Use {}trump add <"quote"> <"True/False">'.format(self.prefix))


def setup(bot):
    bot.add_cog(DiscordTrumpQuote(bot))


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    s = Stats('/')
    print(s.get_table())
    #q = TrumpQuote()
    #q.add_quote('This is a new test', True)
    #print(q.get_result())


