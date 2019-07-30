#!/usr/bin/env python

import csv
import pickle
from flask import Flask, request, jsonify, send_file

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
        return parse_volunteers_from_csv(request)
    elif request.method == 'GET':
        return list_volunteers(request)

def parse_volunteers_from_csv(r):
    return "Not implemented"

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
