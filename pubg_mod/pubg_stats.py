import requests
import config
from prettytable import PrettyTable
import logging
logging.basicConfig(level=logging.INFO)
import json
import time


class StatBoard:
    def __init__(self):
        self.players = self._get_players()
        self.stats = {}
        self.lastupdate = {}
        # check for update on every use
        self.update()
        self.tables = []
        self.header_labels = []

    def built_table(self, region='eu', mode='squad-fpp', season='2018-01', fields=config.interesting_fields):
        try:
            logging.log(20, 'Building Table (%s | %s | %s | %s)' % (region, mode, season, fields))
            t = PrettyTable()
            t.left_padding_width = 0
            t.right_padding_width = 0
            t.title =('%s - %s - %s' % (region.upper(), mode.upper(), season.upper()))
            self._build_headers(fields)
            t.field_names = self.header_labels
            t.align = "r"
            #x.get_string(sortby="Population")
            # oh god runtime
            for player in self.players:
                row = [player]
                for field in fields:
                    for stat in self.stats[player]:
                        if (stat.field == field) and (stat.region == region) and (stat.mode == mode) and (stat.season == season):
                            row.append(stat.display_value)
                if row != [player]:
                    t.add_row(row)
            if t._rows != []:
                #t.field_names = headers
                self.tables.append(t)
                return t
            else:
                logging.log(20, 'No data for specified filters')
                return False
        except:
            logging.log(20, 'There was an error building (%s | %s | %s | %s)' % (region, mode, season, fields))
            return False

    def update(self):
        curr = time.time()
        for player in self.players:
            if player in self.lastupdate:
                if curr - self.lastupdate[player] > 3600:
                    logging.log(20, 'Data for player %s too old, requesting api update' % player)
                    try:
                        self.pull_api(player)
                        self.lastupdate[player] = time.time()
                    except:
                        logging.error('There was an error trying to update %s' % player)
                else:
                    logging.log(20, 'Data of %s is up-to-date' % player)
            else:
                logging.log(20, 'No Data for player %s, requesting api update' % player)
                self.pull_api(player)
                self.lastupdate[player] = time.time()

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
                    self._process_response(data, player)
                    return data
            except:
                logging.log(20, 'There was an error trying to pull apis of %s' % player)

    def _process_response(self, data, player):
        try:
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
                    s = Stat(_region, _mode, _season, _player, _label, _field, _value, _display_value, _category, _updated)
                    _all_stats.append(s)
            self.stats[_player] = _all_stats
            logging.log(20, 'Update for %s completed successfully' % player)
        except:
            logging.log(20, 'There was an error processing the data of {}: {}'.format(player, data))

    def _get_players(self):
        _f = open(config.regpath, 'r')
        _r = _f.read()
        _f.close()
        _p = _r.split('\n')
        logging.log(20, 'Currently registered players %s' % _p)
        return _p

    def _build_headers(self, fields):
        self.header_labels = ['Name']
        for field in fields:
            header = config.header_labels[field]
            self.header_labels.append(header)


class Stat:
    def __init__(self, region, mode, season, player, label, field, value, display_value, category, updated):
        self.region = region
        self.mode = mode
        self.season = season
        self.value = value
        self.label = label
        self.field = field
        self.player = player
        self.display_value = display_value
        self.category = category
        self.updated = updated


if __name__ == "__main__":
    import time
    s = StatBoard()

    s.pull_api('RaZaq')
    #print(stats.built_table('eu', 'squad-fpp', '2017-pre6', config.interesting_fields))
    #built_table(self, region='agg', mode='squad-fpp', season='2017-pre6', fields=['Wins', 'KillDeathRatio']):