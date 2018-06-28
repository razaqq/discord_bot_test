import sqlite3
import traceback
import requests
import json
from prettytable import PrettyTable
from discord.ext import commands
import datetime
import discord
import asyncio
import logging


class WorldCup:
    def __init__(self, workdir, server, api_key):
        self.conn = sqlite3.connect('{}/databases/worldcup.db'.format(workdir))
        self.cursor = self.conn.cursor()
        self.url = 'http://api.football-data.org/v1/competitions/467/fixtures'
        self.pending = []
        self.server = server
        self.api_key = api_key

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
        t.align['Player'] = 'l'

        for p in _res:
            id = p[0]
            points = p[1]
            name = discord.utils.get(self.server.members, id=str(id)).nick
            t.add_row([name, points])
        return t

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
                t.align['Type'] = 'l'
                t.align['Team1'] = 'l'
                t.align['Team2'] = 'l'
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

    def get_bets_by_player(self, player_id, table=False):
        _code = "SELECT * FROM votes WHERE player_id={} ORDER BY game ASC".format(player_id)
        self.cursor.execute(_code)
        _res = self.cursor.fetchall()
        if not table:
            return _res
        else:
            total_rows = len(_res)
            tables = []
            winner = None

            while len(_res) > 0:
                t = PrettyTable()
                t.left_padding_width = 1
                t.right_padding_width = 1
                if len(_res) == total_rows:
                    t.title = 'Your bets'
                t.field_names = ['ID', 'Type', 'Team1', 'Team2', 'Score']
                t.align['Team1'] = 'l'
                t.align['Team2'] = 'l'

                rows = 0
                while True:
                    if rows >= 25 or len(_res) == 0:
                        tables.append(t.get_string())
                        break
                    vote = _res[0]
                    if vote[0] == 999:
                        winner = vote[2]
                        _res.remove(vote)
                        continue
                    score = '{}:{}'.format(vote[4], vote[5])
                    row = [vote[0], vote[1], vote[2], vote[3], score]
                    t.add_row(row)
                    _res.remove(vote)
                    rows += 1
            if winner:
                w = PrettyTable()
                w.left_padding_width = 1
                w.right_padding_width = 1
                w.field_names = ['Your winner bet']
                w.add_row([winner])
                tables.append(w.get_string())
            return tables

    def get_bets_by_game(self, game):
        _code = "SELECT * FROM votes WHERE game={};".format(game)
        self.cursor.execute(_code)
        _res = self.cursor.fetchall()
        return _res

    def get_finished_games(self):
        games = [GameDetails(self._get_game_details(game_id)) for game_id in self.pending]
        self.pending = []
        return games

    def _get_game_details(self, game):
        _code = 'SELECT * FROM games WHERE game="{}";'.format(game)
        self.cursor.execute(_code)
        _res = self.cursor.fetchall()
        if not _res:
            return None
        return _res[0]

    def update_from_json(self):
        headers = {'X-Auth-Token': self.api_key}
        r = requests.get(self.url, headers=headers)
        data = r.json()
        if 'error' in data:
            return
        fixtures = data['fixtures']
        for match in fixtures:
            match_id = fixtures.index(match) + 1
            team1 = match['homeTeamName']
            team2 = match['awayTeamName']
            date = match['date'].replace('Z', '') + 'UTC+00:00'
            result = match['result']
            score = '{}:{}'.format(result['goalsHomeTeam'], result['goalsAwayTeam'])

            status = match['status']
            if status == 'FINISHED':
                finished = True
            else:
                finished = False

            game = GameDetails(self._get_game_details(match_id))
            if not game.finished and finished:
                self.pending.append(match_id)
            _code = 'UPDATE games SET date="{}", team1="{}", team2="{}", score="{}", finished="{}" WHERE game={}' \
                    ''.format(date, team1, team2, score, finished, match_id)
            self.cursor.execute(_code)
            self.conn.commit()

    def update_player_points(self):
        _code = 'DELETE FROM points;'
        self.cursor.execute(_code)
        self.conn.commit()

        games = self.get_game_list()
        player_points = dict()
        for game in games:
            if game.score == 'None:None':
                continue

            bets = self.get_bets_by_game(game.game)
            score = game.score.split(':')
            t1_score = int(score[0])
            t2_score = int(score[1])

            # bonus points for final
            if game.game_details == 'Final':
                if game.finished:
                    winner = game.team1 if int(game.score.split(':')[0]) > int(game.score.split(':')[1]) else game.team2
                    bets = self.get_bets_by_game(999)
                    for bet in bets:
                        player = bet[6]
                        guessed_winner = bet[2]
                        if winner == guessed_winner:
                            if player in player_points:
                                player_points[player] += 6
                            else:
                                player_points[player] = 6

            for bet in bets:
                player = bet[6]
                t1_bet_score = bet[4]
                t2_bet_score = bet[5]
                correct_score = t1_bet_score == t1_score and t2_bet_score == t2_score
                correct_winner = (t1_bet_score > t2_bet_score and t1_score > t2_score) or \
                                 (t1_bet_score < t2_bet_score and t1_score < t2_score) or \
                                 (t1_bet_score == t2_bet_score and t1_score == t2_score)
                if correct_score:
                    if player in player_points:
                        player_points[player] += 3
                    else:
                        player_points[player] = 3
                elif correct_winner:
                    if player in player_points:
                        player_points[player] += 1
                    else:
                        player_points[player] = 1
                else:
                    if player not in player_points:
                        player_points[player] = 0

        for player in player_points:
            self.set_points(player, player_points[player])

    def set_points(self, player, points):
        _code = 'INSERT INTO points VALUES ({}, {})'.format(player, points)
        self.cursor.execute(_code)
        self.conn.commit()

    def _get_flag_emojis_from_json(self):
        r = requests.get(self.url)
        data = r.json()
        teams = data['teams']
        dic = dict()
        for team in teams:
            dic[team['name']] = team['emoji']

        with open('C:/Users/fabio/PycharmProjects/discord_bot/config/worldcup.json', 'w', encoding='utf-8') as wc:
            return json.dump(dic, wc, indent=2)

    def get_group_tables(self):
        def add_points(dic, team, p, played=False):
            if team in dic and played:
                dic[team][0] += p
                dic[team][1] += 1
            elif team not in dic and played:
                dic[team] = [p, 1]
            elif team not in dic and not played:
                dic[team] = [p, 0]

        gptables = []
        for group in ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'):
            self.cursor.execute(
                'SELECT team1, team2, score, finished FROM games WHERE game_type="GROUP"'
                ' AND game_details=?', group
            )
            gpres = self.cursor.fetchall()
            teams = {}
            for res in gpres:
                if res[3] == 'False':
                    add_points(teams, res[0], 0)
                    add_points(teams, res[1], 0)
                    continue
                s = [int(x) for x in res[2].split(':')]
                if s[0] == s[1]:
                    add_points(teams, res[0], 1, True)
                    add_points(teams, res[1], 1, True)
                elif s[0] > s[1]:
                    add_points(teams, res[0], 3, True)
                    add_points(teams, res[1], 0, True)
                else:
                    add_points(teams, res[0], 0, True)
                    add_points(teams, res[1], 3, True)

            t = PrettyTable()
            t.title = 'Group {}'.format(group)
            t.field_names = ['Team', 'Points', 'Games']
            t.align = 'l'
            t.sortby = 'Points'
            t.left_padding_width = 0
            t.right_padding_width = 0
            for team in teams:
                t.add_row([team, teams[team][0], teams[team][1]])

            gptables.append(t.get_string(sortby='Points', reversesort=True))

        strings = []
        for i in range(0, len(gptables), 4):
            s = ''
            t1 = gptables[i].split('\n')
            t2 = gptables[i + 1].split('\n')
            t3 = gptables[i + 2].split('\n')
            t4 = gptables[i + 3].split('\n')
            for j in range(len(t1)):
                s += '{} {} {} {}\n'.format(t1[j], t2[j], t3[j], t4[j])
            strings.append(s)
        return strings

    def bet_winner(self, player_id, team):
        if datetime.datetime.now() > datetime.datetime.strptime('2018-06-30 16:00:00.000000', "%Y-%m-%d %H:%M:%S.%f"):
            return 'Its too late to bet a tournament winner'
        self.cursor.execute('SELECT team1, team2 from games')
        res = self.cursor.fetchall()
        teams = []
        for game in res:
            for t in game:
                if t != '' and t not in teams:
                    teams.append(t)
        if team not in teams:
            return 'That team doesnt exist. Valid teams are: \n {}'.format(teams)
        self.cursor.execute('SELECT team1 FROM votes WHERE game=999 AND player_id=?', (player_id,))
        res = self.cursor.fetchall()
        if len(res) > 0:
            self.cursor.execute('UPDATE votes SET team1=? WHERE game=999 AND player_id=?', (team, player_id))
            self.conn.commit()
            return 'I updated your winner bet from {} to {}'.format(res[0][0], team)
        else:
            self.cursor.execute("INSERT INTO votes (game, team1, player_id) VALUES (999, ?, ?)", (team, player_id))
            self.conn.commit()
            return 'I added your winner bet.'


class GameDetails:
    def __init__(self, details):
        self.game = details[0]
        self.date = details[1]
        self.game_type = details[2]
        self.game_details = details[3]
        self.team1 = details[4]
        self.team2 = details[5]
        self.score = details[6]
        self.finished = (details[7] == 'True')


class DiscordWorldCup:
    def __init__(self, bot):
        self.bot = bot
        self.config = self.load_config(self.bot.workdir)
        self.server = discord.utils.get(self.bot.servers, id=str(self.config['server']))
        self.main_channel = self.server.get_channel(str(self.config['main_channel']))
        self.results_channel = self.server.get_channel(str(self.config['results_channel']))
        self.wc = WorldCup(self.bot.workdir, self.server, self.config['api-token'])
        # bot.loop.create_task(self.start())

    async def start(self):
        await self.bot.wait_until_ready()
        # await self.clear_channel()
        await self.update_channel()

    async def task_run(self):
        await self.bot.wait_until_ready()
        while True:
            try:
                await self.update_channel()
            except Exception as e:
                logging.error(e)
            await asyncio.sleep(30 * 60)

    @staticmethod
    def load_config(workdir):
        with open(workdir + '/config/worldcup.json', 'r', encoding='utf-8') as doc:
            return json.load(doc)

    async def clear_channel(self):
        counter = 0
        async for x in self.bot.logs_from(self.main_channel, limit=50):
            if counter < 50:
                await self.bot.delete_message(x)
                counter += 1
                await asyncio.sleep(1.2)

    async def update_channel(self):
        self.wc.update_from_json()
        self.wc.update_player_points()

        finished = self.wc.get_finished_games()
        for game in finished:
            votes = self.wc.get_bets_by_game(game.game)
            t = PrettyTable()
            t.left_padding_width = 1
            t.right_padding_width = 1
            t.field_names = ['Player', 'Bet']
            t.align['Player'] = 'l'
            for vote in votes:
                nick = discord.utils.get(self.server.members, id=str(vote[6])).nick
                row = [nick, '{}:{}'.format(vote[4], vote[5])]
                t.add_row(row)

            team1_flag = self.config[game.team1]
            team2_flag = self.config[game.team2]
            msg = 'Game just ended!\n' \
                  '{} vs {} : {}\n\n' \
                  '```{}```'.format(team1_flag, team2_flag, game.score, t.get_string())
            await self.bot.send_message(self.results_channel, msg)

        messages = await self.get_messages()
        tables = self.wc.get_game_plan()
        for table in tables:
            m = messages[tables.index(table)]
            await self.bot.edit_message(m, '```' + str(table) + '```')
            await asyncio.sleep(1.2)
        tables = self.wc.get_group_tables()
        for table in tables:
            m = messages[tables.index(table) + 4]
            await self.bot.edit_message(m, '```' + table + '```')
            await asyncio.sleep(1.2)
        await self.bot.edit_message(messages[6], '```' + str(self.wc.get_player_stats()) + '```')
        await asyncio.sleep(1.2)
        msg = 'Commands for FIFA WorldCup 2018:\n\n' \
              '!bet <gameid> <score1>:<score2>, ex: !bet 12 3:3 - to save a vote\n' \
              '!betwizard - for doing them quick and easy\n' \
              '!bets - to see your saved bets\n' \
              '!wcwinner <team> - to bet a winner\n' \
              '!wcupdate - updates tables from api, dont overuse k thx\n\n' \
              'You get 1 point for guessing the correct winner (or draw) and 3 points for the correct score\n' \
              'Means you can get 0, 1 or 3 points per game and 6 points if you guess right tournament winner\n\n' \
              'Tables in this channel will update every 30 minutes, texting is disabled\n' \
              'last update: {}'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        await self.bot.edit_message(messages[7], '```' + msg + '```')

    async def get_messages(self):
        messages = []
        for m_id in self.config['messages']:
            try:
                messages.append(await self.bot.get_message(self.main_channel, str(m_id)))
            except discord.NotFound:
                await self.bot.send_message(self.main_channel, 'Some nerd deleted some of the messages, please fix')
            except discord.Forbidden:
                await self.bot.send_message(self.main_channel, 'I dont have permissions for that!')
            except discord.HTTPException:
                await self.bot.send_message(self.main_channel, 'Discord servers are shit again')
        return messages

    async def on_message(self, message):
        if message.author.bot:
            return
        elif message.channel == self.main_channel:
            await self.bot.delete_message(message)
        # if message.content == 'update' and message.channel == self.channel:
            # await self.clear_channel()
            # await self.update_channel()

    @commands.command(pass_context=True)
    async def bet(self, ctx, game=None, score=None):
        """Bet a score for a game"""
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

    @commands.command()
    async def wcupdate(self):
        """Updates tables etc."""
        msg = await self.bot.say('Updating...')
        await self.update_channel()
        if msg.channel == self.main_channel:
            await asyncio.sleep(3)
            await self.bot.delete_message(msg)

    @commands.command(pass_context=True)
    async def bets(self, ctx):
        """Shows your bets"""
        author = ctx.message.author
        tables = self.wc.get_bets_by_player(int(author.id), True)
        for t in tables:
            await self.bot.send_message(author, '```' + t + '```')

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
            votes = self.wc.get_bets_by_player(author.id)

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

    @commands.command(pass_context=True)
    async def wcwinner(self, ctx, team=None):
        author = ctx.message.author
        if team:
            await self.bot.send_message(author, self.wc.bet_winner(int(author.id), team))
        else:
            await self.bot.send_message(author, 'Usage: !wcwinner <team>')


def setup(bot):
    d = DiscordWorldCup(bot)
    bot.loop.create_task(d.task_run())
    bot.add_cog(d)


if __name__ == '__main__':
    w = WorldCup('.', None, '0ce37e3c659f4f3383e792797c490e5e')
    # print(w._get_game_details(1))
    # print(w.add_bet(23423423, 2, 2, 2))
    # print(str(w.get_player_stats()))
    # w.update_from_json()
    # print(w.pending)
    lala = w.get_bets_by_player(79711959796162560, True)
    # lala.reverse()
    for t in lala:
        print(t)
