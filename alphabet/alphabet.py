# all the imports
import http.client
import json
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
     
app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , alphabet.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'alphabet.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='lemotdepasse'
))
app.config.from_envvar('ALPHABET_SETTINGS', silent=True)

connection = http.client.HTTPConnection('api.football-data.org')
headers = { 'X-Auth-Token': '1e3a1eef83194d64a62b7faaead5fe3b', 'X-Response-Control': 'minified' }
connection.request('GET', '/v1/competitions/434/fixtures', None, headers )
response = json.loads(connection.getresponse().read().decode())

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
	return render_template('page.html')

'''@app.route('/matchday/<id>', methods=['POST'])
def edit(id):
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    cur = db.execute('select id, title, text from entries where id = ?',[id])
    entries = cur.fetchall()
    return render_template('edit.html',entry=entries[0])'''

'''for r in response['fixtures']:
    if r['status'] == 'FINISHED':
        team1 = r['homeTeamName']
        team2 = r['awayTeamName']
        journee= r['matchday']
        date=r['date'].split('T')
        date[1]=date[1].strip(':00Z')
        resultHomeTeam=r['result']['goalsHomeTeam']
        resultAwayTeam=r['result']['goalsAwayTeam']
        print('--------------------------------------------')
        print(str(journee) +' e journée '+' '+str(date[1])+'H')
        print(team1 +' '+str(resultHomeTeam)+' - '+ str(resultAwayTeam)+' '+team2)
    if r['status'] == 'TIMED':
        team1 = r['homeTeamName']
        team2 = r['awayTeamName']
        journee= r['matchday']
        date=r['date'].split('T')
        date[1]=date[1].strip(':00Z')
        print('--------------------------------------------')
        print(str(journee) +'e journée')
        print(team1 +' '+str(date[1])+'H'+' '+team2)'''
