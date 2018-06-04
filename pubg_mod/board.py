import logging
logging.basicConfig(level=logging.INFO)
import time
from prettytable import *
import config
from pubg_mod import database
import requests


class Board:
    def __init__(self):
        self.table = PrettyTable()
        self.updated = 0
        self.players = self.get_players()
        self.db = database.Database()
        self.update()

    def update(self):
        for player in self.players:
            data = self.pull_api(player)
            _player = data['nickname']
            _updated = data['lastUpdated']
            _stats = data['stats']
            _all_stats = []
            for stat in _stats:
                _region = stat['region']
                _season = stat['season']
                _mode = stat['mode']
                _s = stat['stats']
                for field in _s:
                    _label = field['label']
                    _value = field['value']
                    _field = field['field']
                    _display_value = field['displayValue']
                    _category = field['category']
                    self.db._insert('stats', _field, _display_value)
        self.db.commit()

    def get_players(self):
        _f = open(config.regpath, 'r')
        _r = _f.read()
        _f.close()
        _p = _r.split('\n')
        logging.log(20, 'Currently registered players %s' % _p)
        return _p

    def pull_api(self, player=''):
        if player != '':
            try:
                url = 'https://api.pubgtracker.com/v2/profile/pc/' + player
                headers = {'TRN-Api-Key': config.apikey}

                # filters = '?region=' + input_region + '&season=' + config.current_season + '&mode=' + input_match
                response = requests.get(url, headers=headers)
                data = response.json()
                if data:
                    logging.log(20, 'Received data for %s, processing' % player)
                    #self._process_response(data, player)
                    return data
            except:
                logging.log(20, 'There was an error trying to pull apis of %s' % player)


if __name__ == '__main__':
    b = Board()