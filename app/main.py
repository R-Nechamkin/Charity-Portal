import traceback

from flask import Flask, render_template, request, url_for, flash, redirect, jsonify
from flask import Blueprint
from flask_sqlalchemy.session import Session
from sqlalchemy import select
from flask_login import login_required, current_user

from werkzeug.utils import secure_filename

import pandas
import requests
import json
import os

from .util import *
from .database import *
from .models import *
from .secrets import API_KEY, DB_CONNECTOR

main = Blueprint('main', __name__)



@main.route('/')
@main.route('/index')
@login_required
def index():
    return render_template('index.html', message='Welcome ' + current_user.username)


@login_required
@main.route('/email', methods=['GET', 'POST'])
def email():
    if request.method == 'POST':
        email_from = request.form['from']
        if not check_email_address(email_from):
            flash('"From" field must be an email address or a field of type Email')
            return redirect(url_for('main.email'))

        to = request.form['to']
        if not check_email_address(to):
            flash('"To" field must be an email address or a field of type Email')
            return redirect(url_for('main.email'))
        email_body = request.form['email_body']
        subject = request.form['subject']

        for record in current_user.charity.records:
            send_email(email_from=replace_placeholders(email_from, record),
                       to=replace_placeholders(to, record=record),
                       body=replace_placeholders(email_body, record=record),
                       subject=replace_placeholders(subject, record=record))

    field_names = get_field_names(current_user.charity_id)
    return render_template('email.html', fields=field_names)


@login_required
@main.route('/profile')
def profile():
    return render_template('profile.html')


@main.route('/set-up/num-fields', methods=['GET', 'POST'])
@login_required
def fields():
    if request.method == 'POST':
        num_fields = int(request.form.get('num_fields'))
        return redirect('set-up/field-details/' + str(num_fields))

    if not current_user.charity.fields:
        flash('Data storage not set up for this organization. Let\'s configure your storage before inserting data.')
    return render_template('fields.html')


@main.route('/set-up/field-details/<num_fields>', methods=['GET', 'POST'])
@login_required
def field_details(num_fields):
    if request.method == 'POST':
        field_details = []
        for i in range(int(num_fields)):
            field_name = request.form.get(f'field_name_{i}')
            field_type = request.form.get(f'field_type_{i}')
            field_num = i
            field_details.append((field_name, field_type, field_num))
        create_table(field_details, user=current_user)
        return redirect(url_for('main.see_data'))

    return render_template('field_details.html', num_fields=int(num_fields))


@login_required
@main.route('/insert-data')
def insert_data():
    if not current_user.charity.fields:
        return redirect(url_for('main.fields'))

    return render_template('insert-data.html',
                           manual_insertion_link=url_for('main.manual_insert'),
                           import_data_link=url_for('main.import_data'),
                           upload_data_link=url_for('main.upload_data'))


@login_required
@main.route('/insert-data/manual')
def manual_insert():
    return render_template('manual-insert.html')


@login_required
@main.route('/see-data/')
def see_data():
    headers = []
    content = []

    cols = current_user.charity.fields
    headers.append('Record')
    for field in cols:
        headers.append(field.name)

    records = Record.query.filter_by(charity_id=current_user.charity._id).order_by(Record._id)
    for record in records:
        row = []
        row.append(record._id)
        for field in cols:
            data = get_datum(record=record, field=field)
            row.append(data)
        content.append(row)

    return render_template('see-data.html', headers=headers, rows=content)
    
    
@login_required
@main.route('/insert-data/upload', methods=['GET', 'POST'])
def upload_data():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1]
        if not file_ext == '.csv':
            flash('This file is not a CSV file')
            return redirect(url_for('main.upload_data'))

        data = pandas.read_csv(file)
        charity = current_user._id
        headers = Field.query.filter_by(charity_id=charity).order_by(Field.order).all()

        try:
            insert_user_data(charity=current_user.charity, data=data.values, headers=headers)
        # TODO: Really I should only catch database exceptions
        except Exception as e:
            flash('Something went wrong while importing your data. Check your data and try again.')
            print('Error occurred while importing data', traceback.format_exc(), sep='\n')
            return redirect(url_for('main.upload_data'))

        return redirect(url_for('main.see_data'))

    return render_template('upload-data.html')


@login_required
@main.route('/insert-data/import', methods=['GET', 'POST'])
def import_data():

    if request.method == 'POST':
        has_headers = True if request.form.get('has_headers') else False
        try:
            data = get_data_from_api(url=request.form['url'], sheet_index=(int(request.form['sheet_num']) - 1))
            print('We got the data!')
        except Exception as e:
            flash('Something went wrong while trying to access your spreadsheet. Check your internet connection,' +
                  'make sure your sheet is actually shared, and that you pasted the right thing, and try again.')
            print('Error occured while trying to access spreadsheet')
            print(traceback.format_exc())
            return redirect(url_for('main.import_data'))

        if has_headers:
            headers = []
            for col_name in data[0]:
                header = Field.query.filter_by(name=col_name).one()
                headers.append(header)
            data = data[1:]
        else:
            headers = Field.query.filter_by(charity_id =current_user.charity_id).order_by(Field.order).all()

        try:
            insert_user_data(charity=current_user.charity, data=data, headers=headers)
        # TODO: Really I should only catch database exceptions
        except Exception as e:
            flash('Something went wrong while importing your data. Check your data and try again.')
            print(traceback.format_exc())

        return redirect(url_for('main.see_data'))

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
    for user in User.query.all():
        result += user.username + user.email
    return 'hello' + result
