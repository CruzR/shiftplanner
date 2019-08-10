import json
import pickle

with open('static/sisa_shifts.json', 'rt') as f:
    obj = json.load(f)

for shift in obj['shifts']:
    shift['assigned_volunteers'] = []

with open('shifts.pkl', 'wb') as f:
    pickle.dump(obj, f)
