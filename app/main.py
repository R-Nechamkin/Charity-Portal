import traceback

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


def get_data_from_api(url, sheet_index):
    api_begin = "https://sheets.googleapis.com/v4/spreadsheets/" + url + '/'
    api_end = "?key=" + API_KEY['sheets']
    sheet_metadata = requests.get(api_begin + api_end).json()
    sheet_title = sheet_metadata['sheets'][sheet_index]['properties']['title']
    cell_count = sheet_metadata['sheets'][sheet_index]['properties']['gridProperties']
    cell_begin = 'R1c1'
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
    print(current_user.charity_id)
    if ():
        rows = get_data_from_api('18szop7TqllS9pBAyCXZn7LRIvJbPRaw9-MDVcogLh1E')

        return render_template('Grid.html', rows=rows)

    return render_template('index.html', message='No spreadsheet registered for this user')


@login_required
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
            field_num = i
            field_details.append((field_name, field_type, field_num))
        create_table(field_details, user=current_user)
        return redirect(url_for('index'))
    return render_template('field_details.html', num_fields=int(num_fields))


@login_required
@main.route('/insert-data')
def insert_data():
    if not current_user.charity.fields:
        return redirect(url_for('fields'))
        
    return render_template('insert-data.html', manual_insertion_link =  url_for('main.manual_insert'), import_data_link = url_for('main.import_data'))


@login_required
@main.route('/manual-insert')
def manual_insert():
    return render_template('manual-insert.html')


@login_required
@main.route('/import-data', methods=['GET', 'POST'])
def import_data():
    if request.method == 'POST':
        form = request.form.to_dict()

        data = get_data_from_api(url=form['url'], sheet_index=(int(form['sheet_num']) - 1))

        if form['has_headers']:
            headers = data[0]
            data = data[1:]
        else:
            headers = Field.query(Field.name).filter_by(charity_id=current_user.charity_id).order_by(Field.order).all()

        try:
            insert_user_data(charity=current_user.charity, data=data, headers=headers)
        #TODO: Really I should only catch database exceptions
        except Exception as e:
            flash('Something went wrong while importing your file. Check your data and try again.')
            print(traceback.format_exc())

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
