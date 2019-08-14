#!/usr/bin/env python

import codecs
import csv
import itertools
import pickle
import sqlite3
from flask import Flask, request, jsonify, send_file, json, redirect, g

import sisa_welle_1
import sisa_welle_2
import sisa_welle_3

_import_plugins = {
    'sisa_welle_1': sisa_welle_1,
    'sisa_welle_2': sisa_welle_2,
    'sisa_welle_3': sisa_welle_3
}

app = Flask(__name__)


def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS kvstore
            (
                key TEXT UNIQUE NOT NULL,
                value BLOB NOT NULL
             )
             ''')
        db.commit()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('shiftplanner.sqlite')
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def begin_transaction():
    get_db().execute('BEGIN IMMEDIATE TRANSACTION;')

class StorageReadError(Exception):
    pass

def load_value(key):
    c = get_db().cursor()
    c.execute('SELECT value FROM kvstore WHERE key = ?;', (key,))
    row = c.fetchone()
    if row is None:
        raise StorageReadError
    return pickle.loads(row[0])

def store_value(key, value):
    c = get_db().cursor()
    value_bin = sqlite3.Binary(pickle.dumps(value))
    c.execute('INSERT OR REPLACE INTO kvstore VALUES (?, ?);', (key, value_bin))

def commit_transaction():
    get_db().commit()


@app.route('/shifts')
def shifts():
    return send_file('static/shiftviewer.html')

@app.route('/shifts/<int:shift_id>')
def shift(shift_id):
    return send_file('static/shiftdetail.html')

@app.route('/departments')
def departments():
    return send_file('static/departments.html')

@app.route('/volunteers', methods=['GET', 'POST'])
def volunteers():
    if request.method == 'POST':
        return post_volunteers(request)
    elif request.method == 'GET':
        return list_volunteers(request)

def post_volunteers(r):
    if 'volunteers_csv' not in r.files:
        return "No file part"
    file = r.files['volunteers_csv']
    if file.filename == '':
        return "No selected file"
    import_plugin = _import_plugins[r.form['import_plugin']]
    v = parse_volunteers_from_csv(file, import_plugin)
    return redirect(request.url)

def parse_volunteers_from_csv(f, import_plugin):
    f = codecs.getreader('utf-8-sig')(f)
    reader = csv.reader(f, delimiter=';')
    volunteers = []
    with open('static/sisa_departments.json') as f:
        departments = json.load(f)
    departments = {d['name']: d['id'] for d in departments['departments']}
    with open('static/sisa_shifts.json') as f:
        shifts = json.load(f)
    shifts = {s['name']: s['id'] for s in shifts['shifts']}
    for row in itertools.islice(reader, 1, None):
        vol = import_plugin.convert_row(row, departments, shifts, app.logger)
        if vol is not None:
            volunteers.append(vol)

    store_value('volunteers', volunteers)
    commit_transaction()

def list_volunteers(r):
    return send_file('static/volunteers.html')

@app.route('/api/volunteers.json')
def api_volunteers():
    try:
        volunteers = load_value('volunteers')
    except StorageReadError:
        return {'error': 'volunteers.pkl does not exist'}, 500

    return {'volunteers': volunteers}

@app.route('/api/volunteers/<int:vol_id>', methods=['PUT', 'DELETE'])
def api_volunteer(vol_id):
    if request.method == 'DELETE':
        return api_delete_volunteer(vol_id)

    begin_transaction()

    try:
        volunteers = load_value('volunteers')
    except StorageReadError:
        return {'error': 'volunteers.pkl does not exist'}, 500

    try:
        shifts = load_value('shifts')
    except StorageReadError:
        return {'error': 'shifts.pkl does not exist'}, 500

    if not request.is_json:
        app.logger.warn(request)
        return {'error': 'must be json'}, 403

    new_vol = request.get_json()
    vol_index = [i for i, vol in enumerate(volunteers) if vol['id'] == vol_id][0]
    volunteers[vol_index] = new_vol

    assigned_shifts = [s['id'] for s in new_vol['assigned_shifts']]
    for shift in shifts['shifts']:
        if shift['id'] in assigned_shifts:
            if new_vol['id'] not in shift['assigned_volunteers']:
                shift['assigned_volunteers'].append(new_vol['id'])
        elif new_vol['id'] in shift['assigned_volunteers']:
            shift['assigned_volunteers'].remove(new_vol['id'])

    store_value('volunteers', volunteers)
    store_value('shifts', shifts)
    commit_transaction()

    return {'success': True}

def api_delete_volunteer(vol_id):
    begin_transaction()
    try:
        volunteers = load_value('volunteers')
    except StorageReadError:
        return {'error': 'volunteers.pkl does not exist'}, 500

    try:
        shifts = load_value('shifts')
    except StorageReadError:
        return {'error': 'shifts.pkl does not exist'}, 500

    for i, vol in enumerate(volunteers):
        if vol['id'] == vol_id:
            break

    if volunteers[i]['id'] == vol_id:
        del volunteers[i]

    for shift in shifts['shifts']:
        if vol_id in shift['assigned_volunteers']:
            shift['assigned_volunteers'].remove(vol_id)

    store_value('volunteers', volunteers)
    store_value('shifts', shifts)
    commit_transaction()

    return {'success': True}

@app.route('/api/shifts.json')
def api_shifts():
    try:
        shifts = load_value('shifts')
    except StorageReadError:
        return {'error': 'shifts.pkl does not exist'}, 500

    return shifts

@app.route('/api/shifts/<int:shift_id>', methods=['PUT'])
def api_shift(shift_id):
    if not request.is_json:
        return {'error': 'request body must be json'}, 400
    new_shift = request.json

    begin_transaction()
    try:
        shifts = load_value('shifts')
    except StorageReadError:
        return {'error': 'shifts.pkl does not exist'}, 500

    try:
        volunteers = load_value('volunteers')
    except StorageReadError:
        return {'error': 'volunteers.pkl does not exist'}, 500

    for shift in shifts['shifts']:
        if shift['id'] == new_shift['id']:
            shift.update(new_shift)
            break

    for vol in volunteers:
        assigned_shifts = [s['id'] for s in vol['assigned_shifts']]
        if vol['id'] in new_shift['assigned_volunteers']:
            if not new_shift['id'] in assigned_shifts:
                vol['assigned_shifts'].append({'id': new_shift['id'], 'manual': True})
        elif new_shift['id'] in assigned_shifts:
            index = assigned_shifts.index(new_shift['id'])
            del vol['assigned_shifts'][index:index+1]

    store_value('shifts', shifts)
    store_value('volunteers', volunteers)
    commit_transaction()

    return {'success': True}

@app.route('/api/departments.json')
def api_departments():
    return send_file('static/sisa_departments.json')

if __name__ == '__main__':
    app.run()
