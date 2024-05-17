from flask import Flask, render_template, request, url_for, flash, redirect, jsonify
from flask import Blueprint
from flask_sqlalchemy.session import Session
from sqlalchemy import select
from flask_login import login_required, current_user

import requests
import json

from .database import *
from .models import *
from .secrets import API_KEY, DB_CONNECTOR

main = Blueprint('main', __name__)


def get_data_from_api(url, sheet_index, headers=False):
    api_begin = "https://sheets.googleapis.com/v4/spreadsheets/" + url + '/'
    api_end = "?key=" + API_KEY['sheets']
    sheet_metadata = requests.get(api_begin + api_end).json()
    sheet_title = sheet_metadata['sheets'][sheet_index]['properties']['title']
    cell_count = sheet_metadata['sheets'][sheet_index]['properties']['gridProperties']
    if headers:
        cell_begin = 'R2C1'
    else:
        cell_begin = 'R1C1'
    cell_end = cell_count['rowCount'] + 'C' + cell_count['columnCount']
    api_url = api_begin + 'values/' + sheet_title + '!' + cell_begin + ':' + cell_end + api_end
    print('API url:', api_url)
    raw = requests.get(api_url)
    print(raw)
    rows = raw.json()['values']
    print(rows)
    return rows

@main.route('/')
@main.route('/index')
@login_required
def index():
    print(current_user)
    print(current_user.sheet_id)
    if ():
        rows = get_data_from_api('18szop7TqllS9pBAyCXZn7LRIvJbPRaw9-MDVcogLh1E')

        return render_template('Grid.html', rows=rows)

    return render_template('index.html', message='No spreadsheet registered for this user')


@main.route('/profile')
def profile():
    return render_template('profile.html')


@main.route('/fields', methods=['GET', 'POST'])
@login_required
def fields():
    if request.method == 'POST':
        num_fields = int(request.form.get('num_fields'))
        return redirect(url_for('field_details/' + str(num_fields)))
    return render_template('fields.html')


@main.route('/field_details/<num_fields>', methods=['GET', 'POST'])
@login_required
def field_details(num_fields):
    if request.method == 'POST':
        field_details = []
        for i in range(num_fields):
            field_name = request.form.get(f'field_name_{i}')
            field_type = request.form.get(f'field_type_{i}')
            field_details.append((field_name, field_type))
        table_name = current_user.username + 'Table'
        create_table(table_name, field_details, current_user)
        return redirect(url_for('index'))
    return render_template('field_details.html', num_fields=int(num_fields))


@main.route('/insert-data')
def insert_data():
    return render_template('insert-data.html')


@main.route('/insert-data/manual')
def manual_insert():
    return render_template('manual-insert.html')

@main.route('/insert-data/import')
def import_data():
    return render_template('import-data.html')

@main.route('/submitted/<message>')
def show_message(message):
    return render_template('index.html', message=message)


#
# @main.route('/url-for/<user_id>')
# def show_url(user_id):
#     # return render_template('set-up.html', table_data = get_some_data(), message = {})
#     url = get_url_by_user_id(user_id)
#     return redirect('/submitted/' + str(url))
#
#
# @main.route('/debug/see-table/<table_name>')
# def show_table(table_name):
#     table = table_name.capitalize()
#     return render_template('debug.html', message = {}, table_data = get_all_data_from_table(table))
#

@main.route('/debug/orm')
def try_orm():
    def get_users_by_email_domain(domain):
        # Query the User table for all users whose email address ends with the specified domain
        users = User.query.filter(User.email.like(f'%@{domain}*')).all()
        return users

    result = ''
    for user in get_users_by_email_domain(''):
        result += user.username + user.email
    return 'hello' + result
