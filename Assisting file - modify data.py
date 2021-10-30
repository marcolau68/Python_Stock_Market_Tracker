import sqlite3

conn = sqlite3.connect('Stock Market Tracker.db')
c = conn.cursor()

c.execute("DELETE FROM My_Favorites WHERE Code = '388'")
conn.commit()

c.execute("SELECT * FROM My_Favorites")
test = c.fetchall()
print(test)

conn.close()