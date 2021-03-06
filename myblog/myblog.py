#all the imports
import os
import sqlite3 
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

#create the application instance
app = Flask(__name__)
#load config from this file module.py
app.config.from_object(__name__)

#load default config and override config from an enviroment variable
app.config.update(dict(
	DATABASE=os.path.join(app.root_path, 'myblog.db'),
	SECRET_KEY='development key',
	USERNAME='barakaj',
	PASSWORD='rc1TX5RG4t'
	))
app.config.from_envvar('MYBLOG_SETTINGS', silent=True)

#add a method for easy connections to the specified database
def connect_db():
	"""connect to specific database"""
	rv = sqlite3.connect(app.config['DATABASE'])
	rv.row_factory = sqlite3.Row 
	return rv

def init_db():
	db = get_db()
	with app.open_resource('schema.sql', mode='r') as f:
		db.cursor().executescript(f.read())
	db.commit()

@app.cli.command('initdb')
def initdb_command():
	"""Initializes the database"""
	init_db()
	print('Initialized the database')


"""Opens a new database connection if there is none yet
for the current application context
"""
def get_db():
	if not hasattr(g, 'sqlite_db'):
		g.sqlite_db = connect_db()
	return g.sqlite_db








#Closes the database again at the end of the request
@app.teardown_appcontext
def close_db(error):
	if hasattr(g, 'sqlite_db'):
		g.sqlite_db.close()




@app.route('/')
def index():
	return render_template('index.html')

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/contact')
def contact():
	return render_template('contact.html')

@app.route('/home')
def show_entries():
	db = get_db()
	cur = db.execute('select title, text from entries order by id desc')
	entries = cur.fetchall()
	return render_template('show_entries.html', entries=entries)



@app.route('/add', methods=['POST'])
def add_entry():
	if not session.get('logged_in'):
		abort(401)
	db = get_db()
	db.execute('insert into entries(title, text) values (?, ?)',
		[request.form['title'], request.form['text']])

	db.commit()
	flash('New entry was successfully posted')
	return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME']:
			error = 'Invalid username'
		elif request.form['password'] != app.config['PASSWORD']:
			error = 'Invalid password'

		else:
			session['logged_in'] = True
			flash('you were logged in')
			return redirect(url_for('show_entries'))
	return render_template('login.html', error=error)


@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('show_entries'))