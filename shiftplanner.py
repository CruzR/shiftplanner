#!/usr/bin/env python

import codecs
import csv
import itertools
import pickle
from flask import Flask, request, jsonify, send_file, json, redirect

app = Flask(__name__)


@app.route('/shifts')
def shifts():
    return send_file('static/shiftviewer.html')

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
    print("file", r.files['volunteers_csv'])
    v = parse_volunteers_from_csv(file)
    return redirect(request.url)

def parse_volunteers_from_csv(f):
    f = codecs.getreader('utf-8-sig')(f)
    reader = csv.reader(f, delimiter=';')
    volunteers = []
    with open('static/sisa_departments.json') as f:
        departments = json.load(f)
    departments = {d['name']: d['id'] for d in departments['departments']}
    with open('static/sisa_shifts.json') as f:
        shifts = json.load(f)
    shifts = {s['name']: s['id'] for s in shifts['shifts']}

    _ID_COL = 0
    _LASTNAME_COL = 4
    _FIRSTNAME_COL = 5
    _MINOR_COL = 34
    _DEPARTMENTS_COL = 35
    _MINOR_DEPARTMENTS_COL = 37

    def _convert_row(r):
        isminor = False if r[_MINOR_COL] == 'Ja' else True
        if isminor:
            department_col = r[_MINOR_DEPARTMENTS_COL]
        else:
            department_col = r[_DEPARTMENTS_COL]
        desired_departments = []
        for name in department_col.split(', '):
            if name in departments:
                desired_departments.append(departments[name])
            else:
                app.logger.warn("Unknown department: {}".format(repr(name)))
        return {
            'id': int(r[_ID_COL]),
            'lastname': r[_LASTNAME_COL],
            'firstname': r[_FIRSTNAME_COL],
            'isminor': isminor,
            'desired_departments': desired_departments,
            'min_shifts': 2,
            'max_shifts': 2
        }

    for row in itertools.islice(reader, 1, None):
        volunteers.append(_convert_row(row))

    with open('volunteers.pkl', 'wb') as f:
        pickle.dump(volunteers, f)
        f.flush()

def list_volunteers(r):
    return send_file('static/volunteers.html')

@app.route('/api/volunteers.json')
def api_volunteers():
    try:
        f = open('volunteers.pkl', 'rb')
        with f:
            volunteers = pickle.load(f)
            return {'volunteers': volunteers}
    except OSError:
        return {'error': 'volunteers.pkl does not exist'}, 500

@app.route('/api/shifts.json')
def api_shifts():
    return send_file('static/sisa_shifts.json')

@app.route('/api/departments.json')
def api_departments():
    return send_file('static/sisa_departments.json')

if __name__ == '__main__':
    app.run()
