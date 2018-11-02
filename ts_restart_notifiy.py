#!/usr/local/bin/python3.7

from ts3_mod import server
import argparse
import os
import json


class Notify:
    def __init__(self):
        self.workdir = os.path.dirname(os.path.abspath(__file__))
        self.config = self.load_config()

    def load_config(self):
        with open(self.workdir + '/config/main.json', 'r', encoding='utf-8') as doc:
            return json.load(doc)

    def poke_all(self, message):
        ts = server.TS3Server(self.config['ts3ip'], self.config['ts3port'], self.config['ts3sid'])
        ts.login(self.config['ts3user'], self.config['ts3pass'])
        ts.set_client_nick('serveradmin')
        for clid, client in ts.clientlist().items():
            if client['client_type'] == '0':
                ts.clientpoke(clid, message)
        ts.logout()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-time", type=int)
    args = parser.parse_args()
    if args.time:
        plural = 's' if args.time > 1 else ''
        n = Notify()
        n.poke_all("Server Restart in {} Minute{}!".format(args.time, plural))
    else:
        print('Please specify a time with "-time <minutes>"')
