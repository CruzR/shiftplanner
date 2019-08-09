#!/usr/bin/env python

import codecs
import csv
import itertools
import pickle
from flask import Flask, request, jsonify, send_file, json, redirect

import sisa_welle_3

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
    for row in itertools.islice(reader, 1, None):
        volunteers.append(sisa_welle_3.convert_row(row, departments, shifts, app.logger))

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
