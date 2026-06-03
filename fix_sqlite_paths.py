import sqlite3
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--apply', action='store_true')
args = parser.parse_args()

db = 'db.sqlite3'
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute("SELECT id, file FROM documents_document")
rows = cur.fetchall()
proposed = []
for id_, file in rows:
    if not file:
        continue
    new = file
    # normalize repeated prefixes
    while new.startswith('documents/'):
        if new.startswith('documents/documents/'):
            new = new[len('documents/'):]
        else:
            break
    # also handle files/ prefix
    if new.startswith('files/files/'):
        new = new[len('files/'):]
    if new != file:
        proposed.append((id_, file, new))

if not proposed:
    print('No proposed changes')
else:
    print('Proposed changes:')
    for id_, old, new in proposed:
        print(f'id={id_}  {old} -> {new}')
    if args.apply:
        for id_, old, new in proposed:
            cur.execute("UPDATE documents_document SET file = ? WHERE id = ?", (new, id_))
        conn.commit()
        print('Applied changes')

conn.close()
