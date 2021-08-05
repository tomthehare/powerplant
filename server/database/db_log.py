import sqlite3 as db
import sys

con = None

try:
    con = db.connect('test.db')
    
    cur = con.cursor()
    #cur.execute("DROP TABLE Log")
    #cur.execute("CREATE TABLE Log(LogTime DATETIME)")
    cur.execute("INSERT INTO Log VALUES (date('now'))")
    
except db.Error, e:
    print "Error: %s" % e.args[0]
    sys.exit(1)
finally:
    if con:
        con.close()