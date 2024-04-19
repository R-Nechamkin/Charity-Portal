from flask import Flask, render_template, request, url_for, flash, redirect
import sqlite3

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret'


def set_up_database():
    connection = sqlite3.connect('testdb.db')
    with open('testdb.sql') as f:
        connection.executescript(f.read())


def get_db_connection():
  #  set_up_database()
    conn = sqlite3.connect('testdb.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_stuff_from_db():
    conn = get_db_connection()
    return conn.execute('SELECT * FROM User').fetchall()


def get_url_by_user_id(user_id):
    conn = get_db_connection()
    query = """
    SELECT url FROM Spreadsheet
    JOIN User ON Spreadsheet.sheet_id = User.sheet_id
    WHERE user_id = ?"""
    result = conn.execute(query, user_id).fetchone()
    return result['url']


def get_latest_pk_of_spreadsheet():
    conn = get_db_connection()
    query = 'SELECT MAX(sheet_id) AS sheet_id from Spreadsheet'
    return conn.execute(query).fetchone()['sheet_id']


@app.route('/')
def index():
    return render_template('index.html', message='Hello World!')


@app.route('/set-up', methods=('GET', 'POST'))
def set_up():
    user_id = '1'
    if request.method == 'POST':
        url = request.form['sheet_URL']

        if not url:
            flash('Please enter the URL of your sheet')

        else:
            conn = get_db_connection()
            insertion_sql = 'INSERT INTO Spreadsheet (url) VALUES (?)'
            conn.execute(insertion_sql, (url,))
            sheet_id = get_latest_pk_of_spreadsheet()
            relationship_sql = 'UPDATE User SET sheet_id = ? WHERE user_id = ?'
            conn.execute(relationship_sql, (sheet_id, user_id))
            conn.commit()
            return redirect('/url-for/' + user_id)

    message = {
        'title': 'Message 1:',
        'content': get_stuff_from_db()
    }
    return render_template('set-up.html', message=message)


@app.route('/submitted/<message>')
def show_message(message):
    return render_template('index.html', message=message)


@app.route('/url-for/<user_id>')
def show_url(user_id):
    url = get_url_by_user_id(user_id)
    return redirect('/submitted/' + url)