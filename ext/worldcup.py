import sqlite3
import traceback
import requests
import json
from prettytable import PrettyTable
from discord.ext import commands
import datetime
import discord
import asyncio
import asyncio


class WorldCup:
    def __init__(self, workdir, server):
        self.conn = sqlite3.connect('{}/databases/worldcup.db'.format(workdir))
        self.cursor = self.conn.cursor()
        self.json = 'http://api.football-data.org/v1/competitions/467/fixtures'
        self.server = server

    def add_bet(self, player_id, game, team1_score, team2_score):
        _game_details = self._get_game_details(game)
        if not _game_details:
            return 'That game does not exist'
        else:
            g = GameDetails(_game_details)
            try:
                # check if game has started
                d = str(datetime.datetime.now()).split('.')[0].split(' ')

                game_time_data = g.date.split('UTC')[0].split('T')
                game_date = game_time_data[0]

                g_t_s = game_time_data[1].split(':')
                game_time = '{}:{}:{}'.format(int(g_t_s[0]) + 2, g_t_s[1], g_t_s[2])

                if (d[0] > game_date) or (d[0] == game_date and d[1] > game_time):
                    return "Game {} has already started/is over, not accepting any more bets".format(g.game)

                # check if already voted
                _code = 'SELECT team1_score, team2_score FROM votes WHERE player_id={} AND game={};'.format(player_id, game)
                self.cursor.execute(_code)
                _res = self.cursor.fetchall()
                if _res and _res[0]:
                    if _res[0] == (team1_score, team2_score):
                        return 'That is already your current bet'
                    return self._update_bet(g, player_id, team1_score, team2_score)

                # add vote
                _code = 'INSERT INTO votes VALUES ({}, "{}", "{}", "{}", {}, {}, {});'.format(
                    g.game, g.game_details, g.team1, g.team2, team1_score, team2_score, player_id
                )
                self.cursor.execute(_code)
                self.conn.commit()
                return 'Your bet has been added ({} vs {} : {}:{})'.format(g.team1, g.team2, team1_score, team2_score)
            except Exception as e:
                return traceback.format_exc()

    def _update_bet(self, g, player_id, team1_score, team2_score):
        try:
            _code = 'UPDATE votes SET team1_score={}, team2_score={} WHERE player_id={} AND game={};'.format(
                team1_score, team2_score, player_id, g.game
            )
            self.cursor.execute(_code)
            self.conn.commit()
            return 'Your bet has been updated ({} vs {} : {}:{})'.format(g.team1, g.team2, team1_score, team2_score)
        except Exception as e:
            return traceback.format_exc()

    def get_player_stats(self):
        _code = 'SELECT * FROM points ORDER BY points DESC;'
        self.cursor.execute(_code)
        _res = self.cursor.fetchall()
        t = PrettyTable()
        t.left_padding_width = 1
        t.right_padding_width = 1
        t.title = 'Current Bet Points'
        t.field_names = ['Player', 'Points']

        for p in _res:
            id = p[0]
            points = p[1]
            name = discord.utils.get(self.server.members, id=str(id)).nick
            t.add_row([name, points])
        return t

    def get_upcoming_games(self, player_id, game, score):
        pass

    def get_game_plan(self):
        try:
            _code = "SELECT * FROM games ORDER BY game ASC;"
            self.cursor.execute(_code)
            _res = self.cursor.fetchall()
            games = list()
            for r in _res:
                games.append(GameDetails(r))

            tables = []
            table_range = {
                0: 0,
                1: 15,
                2: 31,
                3: 48,
                4: 64
            }
            for i in range(1, 5):
                t = PrettyTable()
                t.left_padding_width = 1
                t.right_padding_width = 1
                if i == 1:
                    t.title = 'WorldCup 2018 Games'
                t.field_names = ['ID', 'Type', 'Team1', 'Team2', 'Score', 'Date', 'Time']
                for g in games:
                    if table_range[i - 1] < g.game <= table_range[i]:
                        if g.game_type == 'GROUP':
                            game_type = 'Group {}'.format(g.game_details)
                        else:
                            game_type = g.game_details
                        date = g.date.split('T')[0]
                        time = g.date.split('T')[1] + 'T' + g.date.split('T')[2]
                        row = [g.game, game_type, g.team1, g.team2, g.score, date, time]
                        t.add_row(row)
                tables.append(t)
            return tables
        except Exception as e:
            return traceback.format_exc()

    def get_game_list(self):
        _code = "SELECT * FROM games ORDER BY game ASC;"
        self.cursor.execute(_code)
        _res = self.cursor.fetchall()
        games = list()
        for r in _res:
            games.append(GameDetails(r))
        return games

    def get_bets(self, player_id, table=False):
        _code = "SELECT * FROM votes WHERE player_id={};".format(player_id)
        self.cursor.execute(_code)
        _res = self.cursor.fetchall()
        if not table:
            return _res
        else:
            t = PrettyTable()
            t.left_padding_width = 1
            t.right_padding_width = 1
            t.title = 'Your bets'
            t.field_names = ['ID', 'Type', 'Team1', 'Team2', 'Score']

            for vote in _res:
                score = '{}:{}'.format(vote[4], vote[5])
                row = [vote[0], vote[1], vote[2], vote[3], score]
                t.add_row(row)

            return t.get_string()

    def get_finished_games(self):
        pass

    def get_goals(self, game):
        pass

    def _get_flag(self, team):
        pass

    def _get_game_details(self, game):
        _code = 'SELECT * FROM games WHERE game="{}";'.format(game)
        self.cursor.execute(_code)
        _res = self.cursor.fetchall()
        if not _res:
            return None
        return _res[0]

    def update_from_json(self):
        r = requests.get(self.json)
        data = r.json()
        fixtures = data['fixtures']
        for match in fixtures:
            match_id = fixtures.index(match) + 1
            team1 = match['homeTeamName']
            team2 = match['awayTeamName']
            date = match['date'].replace('Z', '') + 'UTC+00:00'
            result = match['result']
            score = '{}:{}'.format(result['goalsHomeTeam'], result['goalsAwayTeam'])

            _code = 'UPDATE games SET date="{}", team1="{}", team2="{}", score="{}" WHERE game={}'.format(
                date, team1, team2, score, match_id
            )
            self.cursor.execute(_code)
            self.conn.commit()

    def update_player_points(self):
        # TODO
        pass

    def _get_flag_emojis_from_json(self):
        r = requests.get(self.json)
        data = r.json()
        teams = data['teams']
        dic = dict()
        for team in teams:
            dic[team['name']] = team['emoji']

        with open('C:/Users/fabio/PycharmProjects/discord_bot/config/worldcup.json', 'w', encoding='utf-8') as wc:
            return json.dump(dic, wc, indent=2)


class GameDetails:
    def __init__(self, details):
        self.game = details[0]
        self.date = details[1]
        self.game_type = details[2]
        self.game_details = details[3]
        self.team1 = details[4]
        self.team2 = details[5]
        self.score = details[6]


class DiscordWorldCup:
    def __init__(self, bot):
        self.bot = bot
        self.config = self.load_config(self.bot.workdir)
        self.server = discord.utils.get(self.bot.servers, id=str(self.config['server']))
        self.channel = self.server.get_channel(str(self.config['channel']))
        self.wc = WorldCup(self.bot.workdir, self.server)
        loop = asyncio.get_event_loop()
        loop.create_task(self.start())

    async def start(self):
        await self.bot.wait_until_ready()
        await self.clear_channel()
        await self.update_channel()

    @staticmethod
    def load_config(workdir):
        with open(workdir + '/config/worldcup.json', 'r', encoding='utf-8') as doc:
            return json.load(doc)

    async def clear_channel(self):
        counter = 0
        async for x in self.bot.logs_from(self.channel, limit=50):
            if counter < 50:
                await self.bot.delete_message(x)
                counter += 1
                await asyncio.sleep(1.2)

    async def update_channel(self):
        self.wc.update_from_json()
        tables = self.wc.get_game_plan()
        for table in tables:
            await self.bot.send_message(self.channel, '```' + str(table) + '```')
            await asyncio.sleep(1.2)
        await self.bot.send_message(self.channel, '```' + str(self.wc.get_player_stats()) + '```')
        await asyncio.sleep(1.2)
        msg = 'Commands for FIFA WorldCup 2018:\n\n' \
              '!bet <gameid> <score1>:<score2>, ex: !bet 12 3:3 - to save a vote\n' \
              '!betwizard - for doing them quick and easy\n' \
              '!bets - to see your saved bets\n\n' \
              'You get 1 point for guessing the correct winner (or draw) and 3 points for the correct score\n' \
              'Means you can get 0, 1 or 3 points per game, which results in a total maximum of 192 points\n\n' \
              'Tables in this channel will update every day automatically or when you type "update", ' \
              'texting is disabled'
        await self.bot.send_message(self.channel, '```' + msg + '```')

    async def on_message(self, message):
        if message.author.bot:
            return
        elif message.channel == self.channel:
            await self.bot.delete_message(message)
        if message.content == 'update' and message.channel == self.channel:
            await self.clear_channel()
            await self.update_channel()

    @commands.command(pass_context=True)
    async def bet(self, ctx, game=None, score=None):
        """Bet a score for a game"""
        msg = ctx.message
        player_id = ctx.message.author.id
        if game and score:
            try:
                # await self.bot.delete_message(msg)
                score = score.split(':')
                _res = self.wc.add_bet(player_id, game, int(score[0]), int(score[1]))
                await self.bot.send_message(ctx.message.author, _res)
            except:
                await self.bot.say('Usage: !bet <id> <score1>:<score2>, ex: !bet 24 3:3')
        else:
            await self.bot.say('Usage: !bet <id> <score1>:<score2>, ex: !bet 24 3:3')

    @commands.command(pass_context=True)
    async def bets(self, ctx):
        """Shows your bets"""
        author = ctx.message.author
        vote_table = self.wc.get_bets(author.id, True)
        await self.bot.send_message(author, '```' + vote_table + '```')

    @commands.command(pass_context=True)
    async def betwizard(self, ctx):
        """EZ wizard for betting, your a wizard harry"""
        author = ctx.message.author
        await self.bot.send_message(author, 'Hi, I will guide you through all bets now.\n')
        await self.bot.send_message(author, 'Please enter a range of bets you want to do like 0-64 '
                                            'or type "all" to do all now (valid range: 1-64)\n'
                                            'you have 30 seconds')

        def check(msg):
            if msg:
                a = 'all' in msg.content
                b = '-' in msg.content and len(msg.content) >= 3
                return a or b
            else:
                return False

        msg = await self.bot.wait_for_message(author=author, check=check, timeout=30)

        if check(msg):
            if msg.content == 'all':
                start = 1
                stop = 64
            else:
                start = msg.content.split('-')[0]
                stop = msg.content.split('-')[1]
                try:
                    start = int(start)
                    stop = int(stop)
                except:
                    return await self.bot.send_message(author, 'I only accept numbers as range')

            if start < 1 or stop > 64:
                return await self.bot.send_message(author, 'Only range 1-64 allowed')

            games = self.wc.get_game_list()
            votes = self.wc.get_bets(author.id)

            await self.bot.send_message(author, 'Im going to ask you the bets now.')
            await self.bot.send_message(author, 'Please respond in this format: "2:0" without the "')
            # await self.bot.send_message(author, ' ')

            def check_votes(g):
                v = False
                for vote in votes:
                    if vote[0] == g.game:
                        v = vote
                        break
                return v

            saved = 0
            for g in games:
                if g.game < start:
                    continue
                if g.game > stop:
                    break
                if not g.team1 or not g.team2:
                    return await self.bot.send_message(author, 'OK can only go this far, rest is knockout games '
                                                               'and not known yet. I saved {} bets'.format(saved))
                if len(g.game_details) == 1:
                    game_type = 'Group {}'.format(g.game_details)
                else:
                    game_type = g.game_details
                v = check_votes(g)
                if v:
                    print(v)
                    await self.bot.send_message(author, 'Game {}: {} vs {} ({}) (your current bid is {}:{})'.format(
                        g.game, g.team1, g.team2, game_type, v[4], v[5]
                    ))
                else:
                    await self.bot.send_message(author, 'Game {}: {} vs {} ({})'.format(
                        g.game, g.team1, g.team2, game_type
                    ))
                msg = await self.bot.wait_for_message(author=author, timeout=60)
                if not msg:
                    return await self.bot.send_message(author, 'You took too long, please restart from here')
                try:
                    msg = msg.content.split(':')
                    game1_score = int(msg[0])
                    game2_score = int(msg[1])
                    self.wc.add_bet(author.id, g.game, game1_score, game2_score)
                    saved += 1
                except:
                    return await self.bot.send_message(author, 'What you entered makes no sense, please restart. \n'
                                                               'However i saved the previous {} bets'.format(saved))
            await self.bot.send_message(author, 'Nice we are done! I saved {} bets you gave me'.format(saved))
        else:
            return await self.bot.send_message(author, 'That failed, please restart')


def setup(bot):
    d = DiscordWorldCup(bot)
    bot.add_cog(d)


if __name__ == '__main__':
    w = WorldCup('C:/Users/fabio/PycharmProjects/discord_bot/', None)
    # print(w._get_game_details(1))
    # print(w.add_bet(23423423, 2, 2, 2))
    # print(str(w.get_player_stats()))
    # w.update_from_json()
    print(w.get_bets(187266861031882753, True))
