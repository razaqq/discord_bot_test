import sqlite3
import logging
logging.basicConfig(level=logging.INFO)

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('stats.db')
        self.cursor = self.conn.cursor()

    def select(self, table, fields='*', condition=None):
        if condition:
            code = 'SELECT %s from %s WHERE %s' % (fields, table, condition)
        else:
            code = 'SELECT %s from %s' % (fields, table)
        self.cursor.execute(code)
        return self.cursor.fetchall()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def insert(self, table, fields, values):
        try:
            _fields = ''
            _values = ''
            for field in fields:
                _fields += "'"+field+"',"
            _fields = _fields[:-1]
            for value in values:
                _values += "'"+value+"',"
            _values = _values[:-1]
            code = 'INSERT INTO %s(%s) VALUES (%s)' % (table, _fields, _values)
            self.cursor.execute(code)
        except Exception as e:
            logging.log(20, 'Error inserting into the db: %s' % e)

    def _insert(self, table, field, value):
        try:
            _field = "'"+field+"'"
            _value = "'"+value+"'"
            code = 'INSERT INTO %s(%s) VALUES (%s)' % (table, _field, _value)
            self.cursor.execute(code)
        except Exception as e:
            logging.log(20, 'Error inserting into the db: %s' % e)

    def delete(self, table, condition=None):
        try:
            if condition:
                code = 'DELETE FROM %s WHERE %s' % (table, condition)
            else:
                code = 'DELETE FROM %s' % (table)
            self.cursor.execute(code)
        except:
            logging.log(20, 'Error deleting from the db')

if __name__ == '__main__':
    d = Database()
    print(d.select('stats', '*'))
    #d.insert('stats', ['Name', 'Losses', 'Rating'], ['RaZaq', '428880', '1488'])
    d.commit()
    d.close()


#INSERT INTO Customers (CustomerName, City, Country) VALUES ('Cardinal', 'Stavanger', 'Norway');
#SELECT CustomerName, City FROM Customers;

