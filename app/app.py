from flask import Flask, render_template, request, url_for, flash, redirect
from database import *

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret'


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