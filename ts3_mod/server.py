#!/usr/bin/env python3

import logging
from ts3_mod.protocol import TS3Proto, InvalidArguments
from ts3_mod.defines import *


class TS3Server(TS3Proto):
    def __init__(self, ip=None, port=10011, id=0):
        """
        Abstraction class for TS3 Servers
        @param ip: IP Address
        @type ip: str
        @param port: Port Number
        @type port: int
        """
        TS3Proto.__init__(self)
        self._logger = logging.getLogger(__name__)
        if ip and port:
            if self.connect(ip, int(port)) and int(id) > 0:
                self.use(int(id))

    @property
    def logger(self):
        return self._logger

    def login(self, username, password):
        """
        Login to the TS3 Server
        @param username: Username
        @type username: str
        @param password: Password
        @type password: str
        """

        response = self.send_command('login', keys={'client_login_name': username, 'client_login_password': password})
        return response.is_successful

    def logout(self):
        return self.send_command('logout')

    def serverlist(self):
        """
        Get a list of all Virtual Servers on the connected TS3 instance
        """
        return self.send_command('serverlist')

    def gm(self, msg):
        """
        Send a global message to the current Virtual Server
        @param msg: Message
        @type msg: str
        """
        response = self.send_command('gm', keys={'msg': msg})
        return response.is_successful

    def use(self, id):
        """
        Use a particular Virtual Server instance
        @param id: Virtual Server ID
        @type id: int
        """
        response = self.send_command('use', keys={'sid': id})
        return response.is_successful

    def clientlist(self):
        """
        Returns a clientlist of the current connected server/vhost
        """

        response = self.send_command('clientlist')

        if response.is_successful:
            clientlist = {}
            for client in response.data:
                clientlist[client['clid']] = client
            return clientlist
        else:
            # TODO: Raise a exception?
            self.logger.debug("clientlist - error retrieving client list")
            return {}

    def clientdblist(self):
        """
        Returns a clientlist of the current connected server/vhost
        """

        response = self.send_command('clientdblist')

        if response.is_successful:
            clientdblist = {}
            for client in response.data:
                clientdblist[client['cldbid']] = client
            return clientdblist
        else:
            # TODO: Raise a exception?
            self.logger.debug("clientlist - error retrieving client list")
            return {}

    def channellist(self):
        """
        Returns a channellist of the current connected server/vhost
        """

        response = self.send_command('channellist')

        if response.is_successful:
            channellist = {}
            for channel in response.data:
                channellist[channel['cid']] = channel
            return channellist
        else:
            # TODO: Raise a exception?
            self.logger.debug("channellist - error retrieving channel list")
            return {}

    def clientkick(self, clid=None, cldbid=None, type=REASON_KICK_SERVER, message=None):
        """
        Kicks a user identified by either clid or cldbid
        """

        client = None
        if cldbid:
            clientlist = self.send_command('clientlist')
            for cl in clientlist.data:
                if int(cl['client_database_id']) == cldbid:
                    client = cl['clid']
                    self.logger.debug("clientkick - identified user from clid (%s = %s)" % (cldbid, client))
                    break

            if not client:
                # TODO: we should throw an exception here actually
                self.logger.debug("clientkick - no client with specified cldbid (%s) was found" % cldbid)
                return False
        elif clid:
            client = clid
        else:
            raise InvalidArguments('No clid or cldbid provided')

        if not message:
            message = ''
        else:
            # Kick message can only be 40 characters
            message = message[:40]

        if client:
            self.logger.debug("clientkick - Kicking clid %s" % client)
            response = self.send_command('clientkick', keys={'clid': client, 'reasonid': type, 'reasonmsg': message})
            return response.is_successful

        return False

    def clientpoke(self, clid, message):
        """
        Poke a user identified by clid with the specified message (str)
        """

        response = self.send_command('clientpoke', keys={'clid': clid, 'msg': message})
        return response.is_successful

    def built_channeltree(self):
        _clientlist = self.send_command('clientlist -away -voice').data
        _channellist = self.channellist()
        tree = ''
        if len(_clientlist) == 1:
            return "nobody is here <:feelsbad:345232499103891456>"
        for channel in _channellist.values():
            cid = channel['cid']
            _pid = channel['pid']
            _channel_name = channel['channel_name']
            if _pid == '0':  # Root?
                tree += ('|- ' + _channel_name + '\n')
                for client in _clientlist:
                    _cid = client['cid']
                    client_nickname = client['client_nickname']
                    client_type = client['client_type']
                    client_away = int(client['client_away'])
                    client_input_muted = int(client['client_input_muted'])
                    client_output_muted = int(client['client_output_muted'])
                    if cid == _cid and client_type == '0':
                        tree += ('   -> ' + client_nickname)
                        if client_away or client_input_muted or client_output_muted:
                            tree += '  ['
                        if client_away:  # or client_input_muted or client_output_muted:
                            tree += '💤'
                        if client_input_muted and client_away:
                            tree += ', 🎤-muted'
                        elif client_input_muted:
                            tree += '🎤-muted'
                        if client_output_muted and (client_input_muted or client_away):
                            tree += ', 🔈-muted'
                        elif client_output_muted:
                            tree += '🔈-muted'
                        if client_away or client_input_muted or client_output_muted:
                            tree += ']'
                        tree += '\n'
            else:
                tree += ('   |- ' + _channel_name + '\n')
                for client in _clientlist:
                    _cid = client['cid']
                    client_nickname = client['client_nickname']
                    client_type = client['client_type']
                    client_away = int(client['client_away'])
                    client_input_muted = int(client['client_input_muted'])
                    client_output_muted = int(client['client_output_muted'])
                    if cid == _cid and client_type == '0':
                        tree += ('      -> ' + client_nickname)
                        if client_away or client_input_muted or client_output_muted:
                            tree += '  ['
                        if client_away:  # or client_input_muted or client_output_muted:
                            tree += '💤'
                        if client_input_muted and client_away:
                            tree += ', 🎤-muted'
                        elif client_input_muted:
                            tree += '🎤-muted'
                        if client_output_muted and (client_input_muted or client_away):
                            tree += ', 🔈-muted'
                        elif client_output_muted:
                            tree += '🔈-muted'
                        if client_away or client_input_muted or client_output_muted:
                            tree += ']'
                        tree += '\n'
        tree = '```' + tree + '```'
        return tree

    def get_clids(self, name):
        """Gets the clid to a name in the list of online users"""
        _clientlist = self.clientlist()
        clids = []
        for client in _clientlist.values():
            client_nickname = client['client_nickname']
            if name.lower() == client_nickname.lower():
                clids.append(client['clid'])
        return clids

    def get_dbclids(self, name):
        """Gets the clid to a name in the list of database users"""
        _clientlist = self.clientdblist()
        cldbids = []
        for client in _clientlist.values():
            client_nickname = client['client_nickname']
            if name.lower() == client_nickname.lower():
                cldbids.append(client['cldbid'])
        return cldbids

    def set_client_nick(self, name):
        response = self.send_command('clientupdate', keys={'client_nickname': name})
        return response.is_successful

    def clientmove(self, clid, cid):
        response = self.send_command('clientmove', keys={'clid': clid, 'cid': cid})
        return response.is_successful

    def get_clientinfo(self, clid):
        response = self.send_command('clientinfo', keys={'clid': clid})
        if response.is_successful:
            return response.data[0]
        else:
            return None

    def get_clientdbinfo(self, cldbid):
        response = self.send_command('clientdbinfo', keys={'cldbid': cldbid})
        if response.is_successful:
            return response.data[0]
        else:
            return None

    def is_online(self, cldbid):
        _clientlist = self.clientlist()
        found = False
        for client in _clientlist.values():
            if client['client_database_id'] == cldbid:
                found = True
                break
        return found

    def move_afk(self, timeout, afk_channel):
        _clientlist = self.clientlist()
        for client in _clientlist.values():
            if int(client['client_type']) != 0 or client['cid'] == afk_channel:
                continue
            else:
                idle_time = int(int(self.get_clientinfo(client['clid'])['client_idle_time'])/1000)
                if idle_time > int(timeout):
                    self.sendtextmessage(1, client['clid'], "You have been moved to the afk channel for inactivity")
                    self.clientmove(client['clid'], afk_channel)

    def sendtextmessage(self, targetmode, target, msg):
        response = self.send_command('sendtextmessage', keys={'targetmode': targetmode, 'target': target, 'msg': msg})
        return response.is_successful
