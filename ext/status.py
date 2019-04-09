from matplotlib import pyplot as plt
from matplotlib import dates
import numpy as np
from datetime import datetime, timedelta
import os
import sqlite3
from discord.ext import commands
from discord import File


class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('{}/databases/status.db'.format(self.bot.root_dir))
        self.cursor = self.conn.cursor()

    @staticmethod
    def del_plots():
        if os.path.exists('cpu_load_plot.png'):
            os.remove('cpu_load_plot.png')
        if os.path.exists('cpu_temp_plot.png'):
            os.remove('cpu_temp_plot.png')
        if os.path.exists('net_usage_plot.png'):
            os.remove('net_usage_plot.png')
        if os.path.exists('mem_usage_plot.png'):
            os.remove('mem_usage_plot.png')

    def generate_cpu_load_plot(self):
        self.cursor.execute('SELECT load, time FROM cpu_load ORDER BY time DESC')
        res = self.cursor.fetchall()

        y = np.array([float(y[0]) for y in res])
        x = [datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S.%f') for x in res]

        fig, ax = plt.subplots()

        plt.plot_date(x, y, fmt='x', linestyle=':', linewidth=1, xdate=True, label='Avg CPU Load')

        formatter = dates.DateFormatter('%H:%M')
        ax.xaxis.set_major_formatter(formatter)
        plt.xlabel('UTC+1')
        plt.ylabel('Load in %')
        plt.legend()
        plt.grid(True)
        fig.suptitle('Average CPU Load', fontsize=16)
        fig.set_size_inches(15, 5)
        plt.savefig('cpu_load_plot.png')

    def generate_cpu_temp_plot(self):
        self.cursor.execute('SELECT temp, time FROM cpu_temp ORDER BY time DESC')
        res = self.cursor.fetchall()

        y = np.array([float(y[0]) for y in res])
        x = [datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S.%f') for x in res]

        fig, ax = plt.subplots()

        plt.plot_date(x, y, fmt='x', linestyle=':', linewidth=1, xdate=True, label='CPU Temperature')

        formatter = dates.DateFormatter('%H:%M')
        ax.xaxis.set_major_formatter(formatter)
        plt.xlabel('UTC+1')
        plt.ylabel('CPU Temp in °C')
        plt.legend()
        plt.grid(True)
        fig.suptitle('CPU Temperature', fontsize=16)
        fig.set_size_inches(15, 5)
        plt.savefig('cpu_temp_plot.png')

    def generate_net_usage_plot(self):
        self.cursor.execute('SELECT up, down, time FROM net_usage ORDER BY time DESC')
        res = self.cursor.fetchall()
        up = np.array([float(y[0]) for y in res])
        down = np.array([float(y[1]) for y in res])

        x = [datetime.strptime(x[2], '%Y-%m-%d %H:%M:%S.%f') for x in res]

        f, (ax1, ax2) = plt.subplots(2, sharex=True)

        ax1.plot_date(x, up, 'rx:', linewidth=1, xdate=True, label='Upload')
        ax2.plot_date(x, down, 'cx:', linewidth=1, xdate=True, label='Download')

        f.subplots_adjust(hspace=0.1)

        formatter = dates.DateFormatter('%H:%M')
        ax2.xaxis.set_major_formatter(formatter)

        plt.xlabel('UTC+1')
        ax1.set_ylabel('Traffic in KB/s')
        ax2.set_ylabel('Traffic in KB/s')
        ax1.legend()
        ax2.legend()
        ax1.grid(True)
        ax2.grid(True)
        f.suptitle('Average Network Traffic', fontsize=16)

        f.set_size_inches(15, 5)
        plt.setp([a.get_xticklabels() for a in f.axes[:-1]], visible=False)
        plt.savefig('net_usage_plot.png')

    def generate_mem_usage_plot(self):
        self.cursor.execute('SELECT percent, total, available, time FROM mem_usage ORDER BY time DESC')
        res = self.cursor.fetchall()
        y = np.array([float(y[0]) for y in res])
        y_value = [str(round((float(y[1]) - float(y[2])) / 1000000000, 2)) + ' GB' for y in res]

        x = [datetime.strptime(x[3], '%Y-%m-%d %H:%M:%S.%f') for x in res]

        fig, ax = plt.subplots()

        plt.plot_date(x, y, fmt='x', linestyle=':', linewidth=1, xdate=True, label='Memory used')

        pos = 0
        for x, y in zip(x, y):
            ax.annotate(y_value[pos], xy=(x, y), textcoords='offset pixels', xytext=(0, 40), rotation=45)
            pos += 1

        formatter = dates.DateFormatter('%H:%M')
        ax.xaxis.set_major_formatter(formatter)
        plt.xlabel('UTC+1')
        plt.ylabel('RAM used in %')
        plt.legend()
        plt.grid(True)
        fig.suptitle('Memory Usage', fontsize=16)
        fig.set_size_inches(15, 5)
        plt.savefig('mem_usage_plot.png')

    @commands.command(pass_context=True)
    async def status(self, ctx):
        self.generate_cpu_load_plot()
        self.generate_cpu_temp_plot()
        self.generate_net_usage_plot()
        self.generate_mem_usage_plot()

        await ctx.send(files=[File('cpu_load_plot.png'),
                              File('cpu_temp_plot.png'),
                              File('mem_usage_plot.png'),
                              File('net_usage_plot.png')])
        self.del_plots()


def setup(bot):
    s = Status(bot)
    bot.add_cog(s)


if __name__ == '__main__':
    class Bot:
        def __init__(self):
            self.root_dir = os.path.dirname(os.path.abspath(__file__ + '/..'))

    b = Bot()
    s = Status(b)
    s.generate_cpu_load_plot()
    s.generate_cpu_temp_plot()
    s.generate_net_usage_plot()
    s.generate_mem_usage_plot()
    # s.del_plots()

