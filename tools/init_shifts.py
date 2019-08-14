import json
import pickle
import sqlite3

with open('static/sisa_shifts.json', 'rt') as f:
    obj = json.load(f)

for shift in obj['shifts']:
    shift['assigned_volunteers'] = []

db = sqlite3.connect('shiftplanner.sqlite')
db.execute('INSERT OR REPLACE INTO kvstore VALUES (?, ?)', ('shifts', sqlite3.Binary(pickle.dumps(obj))))
db.commit()
db.close()
