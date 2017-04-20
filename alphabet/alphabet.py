# all the imports
import http.client
import json
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
     
app = Flask(__name__) # create the application instance 
app.config.from_object(__name__) # load config from this file , alphabet.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'alphabet.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('ALPHABET_SETTINGS', silent=True)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')


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


@app.route('/login', methods=['GET','POST'])
def login():
  if request.method == 'POST':
    db = get_db()
    cursor = db.execute('select username from users where username=? and password=?', [request.form['username'], request.form['password']])
    users = cursor.fetchall()
    if users:
  	  session['logged_in'] = True
  return index()


@app.route('/logout')
def logout():
    session['logged_in'] = False
    flash('You were logged out')
    return index()
