import configparser as cp
import os
import logging
import json


class Config(cp.ConfigParser):
    def __init__(self):
        super().__init__()
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.file = os.path.join(self.path, 'config.ini')
        self.restart_needed = False  # hints to the bot if the config needs to be edited first
        self.read_config()
        self.set_attributes()

    def __getattr__(self, item):
        """only gets called for attributes not found"""
        try:
            return self[item]
        except KeyError as e:
            logging.error('KeyError: {}'.format(e))

    def set_attributes(self):
        """Sets config section and keys as attributes"""
        for section in self.sections():
            setattr(self, section, self[section])
            for key in self[section]:
                if self[section][key].startswith('[') and self[section][key].endswith(']'):
                    # load arrays
                    setattr(self[section], key, json.loads(self[section][key]))
                else:
                    setattr(self[section], key, self[section][key])

    def read_config(self):
        """reads the config and checks if its okay"""
        try:
            with open(self.file) as file:
                self.read_file(file)
        except FileNotFoundError as e:
            return self.create_default(e)
        except cp.NoOptionError as e:
            return self.create_default(e)
        except cp.ParsingError as e:
            return self.create_default(e)

    def save(self):
        """saves the current config"""
        for section in self.sections():
            for key in self[section]:
                if isinstance(getattr(self[section], key), list):
                    self[section][key] = json.dumps(getattr(self[section], key))
                else:
                    self[section][key] = str(getattr(self[section], key))
        with open(self.file, 'w') as file:
            self.write(file)

    def create_default(self, error):
        """creates a default config (and backs up old)"""
        self.restart_needed = True
        if not isinstance(error, FileNotFoundError):
            logging.error('Config error:\n{}\nMaking backup and creating default...'.format(error))
            os.rename(self.file, os.path.join(self.path, 'config.ini.bak'))
        else:
            logging.error('No default config found, creating new one...')

        config = cp.ConfigParser()
        config['MAIN'] = {
            'prefix': '!',
            'description': 'All commands below, grouped by category',
            'token': '<your_token_here>',
            'main_guild': 0,
            'enabled_exts': json.dumps(["admin"])
        }
        config['ADMIN'] = {
            'admins': [123543, 43534534]
        }
        config['TS3'] = {
            'ip': '127.0.0.1',
            'port': '10011',
            'user': 'username',
            'pass': 'password',
            'sid': '1',
            'move_afk': True,
            'afk_timeout': '300',
            'afk_channel_id': '1'
        }
        config['BOMB'] = {
            'UBERUSER420': 'tsdbid'
        }
        config['EVE_POLICE'] = {
            'banned_words': 'fozzie,machariel,entosis,ragnarok,ahac,ahacs,blops,aeon,zkill,hedliner,dancul,kb,'
                            'killboard,ratting,nyx,querious,insmother,jita,lazerhawk,isk,lazerhawks,lzhx,goons,'
                            'incursion,fc,cfc,c3,c4,c5,fortizar,astrahus',
            'suspicious_words': 'rent,bil,renting,unrented,pandemic,horde,legion,fort,astra,wh,site,sites,dread,fleet,'
                                'hole,wormhole,wormholes,alliance,deployment,eve,dropped,hotdropped,drop,hotdrop,'
                                'gating,roaming,roam,gate,delve,rent,hawks'

        }
        config['FAKE_NEWS'] = {
            'guild_id': 1234,
            'channel_id': 1234
        }
        config['TRUMP_PIC'] = {
            'api_key': 'abcd',
            'cx': '1234'
        }
        config['TRUMP_TWITTER'] = {
            'consumer_key': 'abcd',
            'consumer_secret': 'abcd',
            'access_token': 'abcd',
            'access_secret': 'abcd',
            'guild_id': 1234,
            'channel_id': 1234
        }
        config['WORLDCUP'] = {
            'guild': 1234,
            'main_channel': 1234,
            'results_channel': 1234,
            'messages': [1234, 1234, 1234],
            'api-token': '1234',

            'Russia': ':flag_ru:',
            'Saudi Arabia': ':flag_sa:',
            'Egypt': ':flag_eg:',
            'Uruguay': ':flag_uy:',
            'Portugal': ':flag_pt:',
            'Spain': ':flag_es:',
            'Morocco': ':flag_ma:',
            'Iran': ':flag_ir:',
            'France': ':flag_fr:',
            'Australia': ':flag_au:',
            'Peru': ':flag_pe:',
            'Denmark': ':flag_dk:',
            'Argentina': ':flag_ar:',
            'Iceland': ':flag_is:',
            'Croatia': ':flag_hr:',
            'Nigeria': ':flag_ng:',
            'Brazil': ':flag_br:',
            'Switzerland': ':flag_ch:',
            'Costa Rica': ':flag_cr:',
            'Serbia': ':flag_rs:',
            'Germany': ':flag_de:',
            'Mexico': ':flag_mx:',
            'Sweden': ':flag_se:',
            'Korea Republic': ':flag_kr:',
            'Belgium': ':flag_be:',
            'Panama': ':flag_pa:',
            'Tunisia': ':flag_tn:',
            'England': ':flag_gb:',
            'Poland': ':flag_pl:',
            'Senegal': ':flag_sn:',
            'Colombia': ':flag_co:',
            'Japan': ':flag_jp:'
        }
        with open(self.file, 'w') as file:
            config.write(file)


if __name__ == '__main__':
    c = Config()
    # print(c.MAIN)
    # print(c.MAIN.token)
    # print(c.TS3.ip)
    print(c.restart_needed)
