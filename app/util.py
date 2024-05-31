import re

import requests
from flask_login import current_user

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from . import API_KEY
from .models import *
from .database import get_datum

placeholder_pattern = re.compile(r'<<(\w[ \w]*)>>')
email_pattern = re.compile(
    r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
)

def check_email_format(email: str) -> bool:
    return email_pattern.fullmatch(email)

def data_from_google_sheets(url, sheet_index):
    api_begin = "https://sheets.googleapis.com/v4/spreadsheets/" + url + '/'
    api_end = "?key=" + API_KEY['sheets']
    sheet_metadata = requests.get(api_begin + api_end).json()
    sheet_title = sheet_metadata['sheets'][sheet_index]['properties']['title']
    cell_count = sheet_metadata['sheets'][sheet_index]['properties']['gridProperties']
    cell_begin = 'R1C1'
    cell_end = 'R' + str(cell_count['rowCount']) + 'C' + str(cell_count['columnCount'])
    api_url = api_begin + 'values/' + sheet_title + '!' + cell_begin + ':' + cell_end + api_end
    print('API url:', api_url)
    raw = requests.get(api_url)
    print(raw)
    rows = raw.json()['values']
    print(rows)
    return rows


def replace_placeholders(text: str, record: Record):
    # Define a regular expression to find all placeholders
    # Find all placeholders in the email text
    placeholders = placeholder_pattern.findall(text)

    placeholder_values = {}

    for placeholder in placeholders:
        # Find the field associated with the placeholder
        field = Field.query.filter_by(name=placeholder, charity_id=current_user.charity_id).first()
        if field:
            datum = get_datum(record=record, field=field)
            placeholder_values[placeholder] = datum

    # Replace all placeholders in the email text with their corresponding values
    for placeholder, value in placeholder_values.items():
        text = text.replace(f'<<{placeholder}>>', str(value))

    return text


def check_email_address(text: str) -> bool:
    if placeholder_pattern.match(text):
        return True
    elif email_pattern.match(text):
        return True
    else:
        return False


def replace_placeholder_email_address(text: str, record: Record):
    placeholder = placeholder_pattern.search(text)
    if placeholder:
        field = Field.query.filter_by(name=placeholder, charity_id=current_user.charity_id).first()
        if field.data_type == 'EMAIL':
            return get_datum(record=record, field=field)
        else:
            raise Exception(f'Field is not an email field: {field.data_type}')
    return text



def send_email(email_from, to, subject, body):
    print_email(email_from, to, subject, body)
    message = Mail(
        from_email='from_email@example.com',
        to_emails='to@example.com',
        subject='Sending with Twilio SendGrid is Fun',
        html_content='<strong>and easy to do anywhere, even with Python</strong>')
    try:
        sg = SendGridAPIClient(API_KEY['email'])
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)
        raise Exception('Something went wrong while sending the email')


def print_email(email_from, to, subject, body):
    print('Sending email:')
    print('From:', email_from)
    print('To:', to)
    print('Subject:', subject)
    print('Body:', body)
