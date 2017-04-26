# all the imports
import http.client
import json
import os
import sqlite3
from datetime import date, datetime
import datetime
import time
import locale 
locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')

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
    matchdaynumber = int(request.args["matchday"]) if "matchday" in request.args else 1
    urlusername = str(request.args["username"]) if "username" in request.args else None
    db = get_db()
    currentuser = urlusername or session['user']
    cursor_db = db.execute('select username from users')

    cursor_db_username = db.execute('select username from users')
    resultusername = [row["username"] for row in cursor_db_username]
    username = cursor_db_username.fetchall()
    
    cursor_uid = db.execute('select u_id from users where username = ?',(currentuser,))
    resultuid = [row["u_id"] for row in cursor_uid]
    
    cursor_matchid = db.execute('select match_id from user_bets where u_id = ?',(resultuid[0],))
    resultset = [row["match_id"] for row in cursor_matchid]
    
    cursor_outcome = db.execute('select outcome from user_bets where u_id = ?',(resultuid[0],))
    resultbet = [row["outcome"] for row in cursor_outcome]
    
    connection_maindatas = http.client.HTTPConnection('api.football-data.org')
    connection_otherdatas = http.client.HTTPConnection('api.football-data.org')
    headers = { 'X-Auth-Token': '1e3a1eef83194d64a62b7faaead5fe3b', 'X-Response-Control' : 'minified' }
    connection_maindatas.request('GET', '/v1/competitions/434', None, headers )
    connection_otherdatas.request('GET', '/v1/competitions/434/fixtures', None, headers )
    
    response_maindatas = json.loads(connection_maindatas.getresponse().read().decode())
    response_otherdatas = json.loads(connection_otherdatas.getresponse().read().decode())
    fixtures_datas = response_otherdatas['fixtures']
    matchid = response_otherdatas['fixtures'][0]['id']
    currentmatchday = int(request.args['matchday']) or response_maindatas['currentMatchday']
    
    users = cursor_db.fetchall()
    
    for fixture_data in fixtures_datas: 
      matchdate = fixture_data['date'][0:10]
      Date = datetime.datetime.strptime(matchdate, '%Y-%m-%d').strftime('%A %d %B %Y')
      matchtime = fixture_data['date'][11:19]
      Time = datetime.datetime.strptime(matchtime, '%H:%M:%S').strftime('%H' + 'h' + '%M')
      fixture_data["Date"]=Date
      fixture_data["Time"]=Time

    print(resultusername)
    print(resultuid)
    print(resultset)
    print(resultbet)
   
    return render_template('page.html', urlusername=urlusername, users=users, matchdaynumber=matchdaynumber, numberofmatchdays=response_maindatas['numberOfMatchdays'], currentmatchday=currentmatchday, competitions=response_maindatas['caption'], fixtures_datas=fixtures_datas, Date=Date, Time=Time, resultset=resultset, resultbet=resultbet, currentuser=currentuser)

@app.route('/login', methods=['GET','POST'])
def login():
  if request.method == 'POST':
    db = get_db()
    cursor = db.execute('select username from users where username = ? and password = ?', [request.form['username'], request.form['password']])
    users = cursor.fetchall()
    if users:
        connected_username = users[0]['username']
        session['user'] = connected_username
        session['logged_in'] = True
    else:
      flash('Mauvais identifiant ou mot de passe')
  return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session['logged_in'] = False
    flash('Vous êtes déconnectés !')
    return redirect(url_for('index'))
   
@app.route('/bet/<int:match_id>', methods=['POST'])
def bet(match_id):
    db = get_db()
    cursor_username = db.execute('select u_id from users where username = ?',(session['user'],))
    usernamedb = cursor_username.fetchall()
    if usernamedb:
        outcome = request.form['result']
        u_id=usernamedb[0]['u_id']
        cursor_username = db.execute('insert into user_bets (u_id, match_id, outcome) values (?, ?, ?)',(u_id, match_id, outcome))
        db.commit()
    return redirect(request.referrer)
