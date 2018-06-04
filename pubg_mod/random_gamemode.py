import random
import sqlite3
from config import pubg_db


class RandomGenerator:
    def __init__(self, players=None):
        self.players = players
        # sqlite
        self.conn = sqlite3.connect(pubg_db)
        self.cursor = self.conn.cursor()

    def get_random_rule(self):
        _code = 'SELECT * FROM rules ORDER BY RANDOM() LIMIT 1;'
        self.cursor.execute(_code)
        _res = self.cursor.fetchall()[0]
        rule = _res[0]
        return rule

    def get_random_player(self):
        player = random.choice(self.players)
        return player

    def set_extra_players(self, owner, rule):
        needed = rule.count('<player>')
        random_players = []

        if needed > len(self.players) - 1:
            return None
        else:
            while needed > 0:
                random_player = self.get_random_player()
                while (random_player == owner) or (random_player in random_players):
                    random_player = self.get_random_player()
                random_players.append(random_player)
                needed -= 1

            for p in random_players:
                rule = rule.replace('<player>', p, 1)

            return rule

    def generate_rules(self):
        rules = []
        for player in self.players:
            rule = self.get_random_rule()
            rule = self.set_extra_players(player, rule)

            while rule is None:  # more needed random players than total players
                rule = self.get_random_rule()
                rule = self.set_extra_players(player, rule)

            rules.append((player, rule))
            # shuffle the array
            random.shuffle(rules)
        return rules

    def add_rule(self, rule):
        _code = 'INSERT INTO rules VALUES ("{}")'.format(rule)
        self.cursor.execute(_code)
        self.conn.commit()

    def get_list(self, string=False):
        _code = 'SELECT * FROM rules;'
        self.cursor.execute(_code)
        _res = self.cursor.fetchall()
        rules = []
        for _r in _res:
            rules.append(_r[0])
        if string:
            string = ''
            for _r in rules:
                string += '- ' + _r + '\n'
            return string
        else:
            return rules

if __name__ == '__main__':
    import doctest
    doctest.testmod()

    players = ['Prom', 'Perry', 'Nyn', 'Devon']
    r = RandomGenerator(players)
    print(r.get_list(True))
