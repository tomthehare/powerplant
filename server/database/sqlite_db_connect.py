import sqlite3
import sys

con = None

try:
    con = sqlite3.connect('test.db')
    
    cur = con.cursor()
    cur.execute('SELECT SQLITE_VERSION()')
    
    data = cur.fetchone()
    
    print("SQLite Version: %s " % data)
    
except sqlite3.Error as e:
    print("Error %s:" % e.args[0])
    sys.exit(1)
finally:
    if con:
        con.close()
