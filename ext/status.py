import discord
from discord.ext import commands
import time
from ts3_mod import server
from requests import get
import json
import cpuinfo
import os
import socket
import random
import select
import struct


class Status:
    def __init__(self, bot):
        self.bot = bot
        self.config = self.config_load()

    def config_load(self):
        with open('config/main.json', 'r', encoding='utf-8') as doc:
            return json.load(doc)

    @commands.command()
    async def status(self):
        """Gives system information"""
        _start = int(round(time.time() * 1000))
        ip = get('https://api.ipify.org').text
        try:
            ts = server.TS3Server(self.config['ts3ip'], self.config['ts3port'], self.config['ts3sid'])
            ts.login(self.config['ts3user'], self.config['ts3pass'])
            status = 'up'
        except:
            status = 'down'

        cpuinf = cpuinfo.get_cpu_info()

        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            restart_seconds = 86400 - uptime_seconds
            uptime_string = time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))
            restart_string = time.strftime("%H:%M:%S", time.gmtime(restart_seconds))

        res = os.popen('vcgencmd measure_temp').readline()
        cpu_temp = res.replace("temp=", "").replace("'C\n", "")

        embed = discord.Embed(title="TS3", url="http://perryswift.tk/ts3.html", color=0x00ff00)
        embed.add_field(name='Domain', value='perryswift.tk', inline=True)
        embed.add_field(name='IP & Port (untill restart)', value=ip + ':9987', inline=True)
        embed.add_field(name='TS3 Status', value=status, inline=True)
        embed.add_field(name='Ping (to google.com)', value=('{}ms'.format(ping('google.com'))), inline=True)
        embed.add_field(name='Arch', value=cpuinf['arch'], inline=True)
        embed.add_field(name='Processor', value=cpuinf['brand'], inline=True)
        embed.add_field(name='CPU-Clock', value=cpuinf['hz_actual'], inline=True)
        embed.add_field(name='Bits', value=cpuinf['bits'], inline=True)
        embed.add_field(name='Cores', value=cpuinf['count'], inline=True)
        embed.add_field(name='CPU-Temp', value=cpu_temp + ' Â°C', inline=True)
        embed.add_field(name='Uptime', value=uptime_string, inline=True)
        embed.add_field(name='Reboot in', value=restart_string, inline=True)
        runtime = int(round(time.time() * 1000)) - _start
        embed.set_footer(text=("generated in %sms" % runtime))
        await self.bot.say(embed=embed)

    def chk(self, data):
        x = sum(x << 8 if i % 2 else x for i, x in enumerate(data)) & 0xFFFFFFFF
        x = (x >> 16) + (x & 0xFFFF)
        x = (x >> 16) + (x & 0xFFFF)
        return struct.pack('<H', ~x & 0xFFFF)

    def ping(self, addr, timeout=1, number=1, data=b''):
        with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as conn:
            payload = struct.pack('!HH', random.randrange(0, 65536), number) + data

            conn.connect((addr, 80))
            conn.sendall(b'\x08\0' + self.chk(b'\x08\0\0\0' + payload) + payload)
            start = time.time()
            start_ms = int(round(time.time() * 1000))

            while select.select([conn], [], [], max(0, start + timeout - time.time()))[0]:
                data = conn.recv(65536)
                if len(data) < 20 or len(data) < struct.unpack_from('!xxH', data)[0]:
                    continue
                if data[20:] == b'\0\0' + self.chk(b'\0\0\0\0' + payload) + payload:
                    return int(round(time.time() * 1000)) - start_ms


def setup(bot):
    bot.add_cog(Status(bot))
