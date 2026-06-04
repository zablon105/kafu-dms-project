import sqlite3

conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()
cur.execute('SELECT id, title, file FROM documents_document ORDER BY id')
rows = cur.fetchall()
for row in rows:
    print(row)
conn.close()
