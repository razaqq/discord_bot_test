import psutil
import sqlite3
from datetime import date, datetime
import time


class SystemInfo:
    def __init__(self):
        self.conn = sqlite3.connect('SystemInfo.db')
        self.cursor = self.conn.cursor()
        self.create_tables()

    def __del__(self):
        self.conn.close()

    def create_tables(self):
        self.cursor.execute('CREATE TABLE IF NOT EXISTS net_usage (up TEXT, down TEXT, time DATETIME PRIMARY KEY)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS mem_usage (total TEXT, available TEXT, percent TEXT, '
                            'time DATETIME PRIMARY KEY)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS cpu_load (load TEXT, time DATETIME PRIMARY KEY)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS cpu_temp (temp TEXT, time DATETIME PRIMARY KEY)')
        self.conn.commit()

    def insert_data(self):
        net_usage = self.get_net_usage('Ethernet')
        self.cursor.execute('INSERT INTO net_usage VALUES (?, ?, ?)', [net_usage[0], net_usage[1], datetime.now()])
        mem_usage = self.get_mem_usage()
        self.cursor.execute('INSERT INTO mem_usage VALUES (?, ?, ?, ?)', [mem_usage.total, mem_usage.available,
                                                                          mem_usage.percent, datetime.now()])
        self.cursor.execute('INSERT INTO cpu_load VALUES (?, ?)', [self.get_cpu_load(), datetime.now()])
        # self.cursor.execute('INSERT INTO cpu_temp VALUES (?, ?)', [self.get_cpu_temp(), datetime.now()])
        self.conn.commit()

    @staticmethod
    def get_net_usage(adapter_name):
        net_usage = psutil.net_io_counters(pernic=True)[adapter_name]
        t0 = time.time()
        bytes_sent = net_usage.bytes_sent
        bytes_recv = net_usage.bytes_recv

        time.sleep(10)

        net_usage = psutil.net_io_counters(pernic=True)[adapter_name]
        t1 = time.time()
        sent = bytes_sent - net_usage.bytes_sent
        recv = bytes_recv - net_usage.bytes_recv

        ul = sent / (t0 - t1) / 1000.0
        dl = recv / (t0 - t1) / 1000.0

        return [ul, dl]

    @staticmethod
    def get_mem_usage():
        return psutil.virtual_memory()

    @staticmethod
    def get_cpu_load():
        load = 0
        for x in range(5):
            load += psutil.cpu_percent(interval=1)
        return round(load / 5, 2)

    @staticmethod
    def get_cpu_temp():
        return psutil.sensors_temperatures(False)['cpu-thermal'][0].current


if __name__ == '__main__':
    s = SystemInfo()
    s.insert_data()
