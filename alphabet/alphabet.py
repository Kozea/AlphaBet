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
    DATABASE=os.path.join(app.root_path, 'alphabet.db')
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
    if not session.get('logged_in'):
	    return render_template('page.html')
    else:
	    return "Hello Boss!"


@app.route('/login', methods=['GET','POST'])
def login():
  db = get_db().cursor()
  error = None
  if request.method == 'POST':
    if request.form['username'] != db.execute('SELECT username FROM users WHERE username=?', (request.form['username'],)).fetchone()['username']:
      error = 'Invalid username. Username text was: ' + request.form['username']
    elif request.form['password'] != db.execute('SELECT password FROM users WHERE username=? AND password=?', (request.form['username'], request.form['password'],)).fetchone():
      error = 'Invalid password'
    else:
      session['logged_in'] = True
      flash('You were logged in')
      return redirect(url_for('index'))
  return render_template('page.html', error=error)


@app.route('/logout')
def logout():
    session['logged_in'] = False
    return index()
