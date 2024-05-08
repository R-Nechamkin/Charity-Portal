from flask import Flask, render_template, request, url_for, flash, redirect
from flask import Blueprint
from flask_sqlalchemy.session import Session
from sqlalchemy import select

from .database import *
from .models import *

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html', message='Hello World!')


@main.route('/profile')
def profile():
    return render_template('profile')


@main.route('/set-up', methods=('GET', 'POST'))
def set_up():
    user_id = '1'
    if request.method == 'POST':
        url = request.form['sheet_URL']

        if not url:
            flash('Please enter the URL of your sheet')

        else:
            conn = get_db_connection()
            insertion_sql = 'INSERT INTO Spreadsheets (url) VALUES (?)'
            conn.execute(insertion_sql, (url,))
            sheet_id = get_latest_pk_of_spreadsheet()
            relationship_sql = 'UPDATE Users SET sheet_id = ? WHERE user_id = ?'
            conn.execute(relationship_sql, (sheet_id, user_id))
            conn.commit()
            return redirect('/url-for/' + str(user_id))

    message = {
        'title': 'Message 1:',
        'content': get_stuff_from_db()
    }
    return render_template('set-up.html', message=message)


@main.route('/submitted/<message>')
def show_message(message):
    return render_template('index.html', message=message)


@main.route('/url-for/<user_id>')
def show_url(user_id):
    # return render_template('set-up.html', table_data = get_some_data(), message = {})
    url = get_url_by_user_id(user_id)
    return redirect('/submitted/' + str(url))


@main.route('/debug/see-table/<table_name>')
def show_table(table_name):
    table = table_name.capitalize()
    return render_template('debug.html', message = {}, table_data = get_all_data_from_table(table))


@main.route('/debug/orm')
def try_orm():
    # def get_users_by_email_domain(domain):
    #     # Query the User table for all users whose email address ends with the specified domain
    #     users = User.query.filter(User.email.like(f'%@{domain}*')).all()
    #     return users
    #
    # result = ''
    # for user in get_users_by_email_domain(''):
    #     result += user.username + user.email
    return 'hello' + get_data(application_id= 1)