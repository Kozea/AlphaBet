# all the imports
import http.client
import json
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
     
app = Flask(__name__) # create the application instance 
app.config.from_object(__name__) # load config from this file , alphabet.py


@app.route('/')
def index():
    connection_maindatas = http.client.HTTPConnection('api.football-data.org')
    connection_otherdatas = http.client.HTTPConnection('api.football-data.org')
    headers = { 'X-Auth-Token': '1e3a1eef83194d64a62b7faaead5fe3b', 'X-Response-Control': 'minified' }
    connection_maindatas.request('GET', '/v1/competitions/434', None, headers )
    connection_otherdatas.request('GET', '/v1/competitions/434/fixtures', None, headers )
    response_maindatas = json.loads(connection_maindatas.getresponse().read().decode())
    response_otherdatas = json.loads(connection_otherdatas.getresponse().read().decode())
    return render_template('page.html', currentmatchday=response_maindatas['currentMatchday'], competitions=response_maindatas['caption'],fixtures_datas=response_otherdatas['fixtures'])
