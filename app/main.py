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
    print(current_user)
    print(current_user.charity_id)
    if ():
        rows = data_from_google_sheets('18szop7TqllS9pBAyCXZn7LRIvJbPRaw9-MDVcogLh1E')

        return render_template('Grid.html', rows=rows)

    return render_template('index.html', message='No spreadsheet registered for this user')

@login_required
@main.route('/email/', methods =['GET', 'POST'])
def email():
    if request.method == 'POST':
        to = request.form['to']
        if not check_email_address(to):
            flash('To field must be an email address or a field of type Email')
            print('To field must be an email address or a field of type Email')
            return redirect(url_for('main.email'))
        email_body = request.form['email_body']
        subject = request.form['subject']

        for record in current_user.charity.records:
            send_email(to=replace_placeholders(to, record=record),
                       body=replace_placeholders(email_body, record=record),
                       subject=replace_placeholders(subject, record=record))
        return redirect(url_for('main.index'))

    field_names = get_field_names(current_user.charity)
    return render_template('email.html', fields = field_names)



@login_required
@main.route('/profile')
def profile():
    return render_template('profile.html')


@main.route('/fields', methods=['GET', 'POST'])
@login_required
def fields():
    if request.method == 'POST':
        num_fields = int(request.form.get('num_fields'))
        return redirect('/field_details/' + str(num_fields))
        
    
    if not current_user.charity.fields:
        flash('Data storage not set up for this organization. Let\'s configure your storage before inserting data.')
    return render_template('fields.html')


@main.route('/field_details/<num_fields>', methods=['GET', 'POST'])
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
        return redirect(url_for('main.index'))
        
    return render_template('field_details.html', num_fields=int(num_fields))


@login_required
@main.route('/insert-data')
def insert_data():
    if not current_user.charity.fields:
        return redirect(url_for('main.fields'))
        
    return render_template('insert-data.html',
        manual_insertion_link =  url_for('main.manual_insert'), import_data_link = url_for('main.import_data'), upload_data_link = url_for('main.upload_data'))


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

    records = Record.query.filter_by(charity_id=current_user.charity.charity_id).order_by(Record.record_id)
    for record in records:
        row = []
        row.append(record.record_id)
        for field in cols:
            data = get_datum(record =record, field=field)
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
        charity = current_user.charity_id
        headers = Field.query.filter_by(charity_id=charity).all()
        
        try:
            insert_user_data(charity=current_user.charity, data=data.values, headers=headers)
        #TODO: Really I should only catch database exceptions
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
        form = request.form.to_dict()
        
        try:
            data = data_from_google_sheets(url=form['url'], sheet_index=(int(form['sheet_num']) - 1))
        except:
            flash('Something went wrong while trying to access your spreadsheet. Check your internet connection,' +
                'make sure your sheet is actually shared, and that you pasted the right thing, and try again.')
            print(traceback.format_exc())
            return redirect(url_for('main.import_data'))

        if form['has_headers']:
            headers = []
            for col_name in data[0]:
                header = Field.query(Field.name == col_name).one()
                headers.append(header)
            data = data[1:]
        else:
            headers = db.session.query(Field.name).filter(Field.charity_id==current_user.charity_id).order_by(Field.order).all()

        try:
            insert_user_data(charity=current_user.charity, data=data, headers=headers)
        #TODO: Really I should only catch database exceptions
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
