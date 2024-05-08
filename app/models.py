from sqlalchemy import text
from sqlalchemy.orm import relationship
from flask_login import UserMixin

from app import db
from app.database import get_db_connection
from app import *

class Spreadsheet:

    def __init__(self, id):
        self.id = id

    def __init__(self, id, url):
        self.id = id
        self.url = url


def get_data(user_id):
    # create a new SQLAlchemy session
    session = db.session()

    # create a SQL statement to get all data for the user with the given ID
    sql = text("SELECT * FROM Users WHERE user_id = :user_id")
    result = session.execute(sql, {"user_id": user_id})

    # convert the SQL result to a list of dictionaries
    user_data = [dict(row) for row in result]

    # close the session
    session.close()

    # return the user data
    return user_data


class User(UserMixin):

    def __init__(self, user_id):
        self.id = user_id

    def __init__(self, user_id, username, password):
        self.id = user_id
        self.username = username
        self.password = password


def get_data(application_id):

    # create a new SQLAlchemy session
    # session = db.session()
    #
    # # create a SQL statement to get all data for the user with the given ID
    sql = 'SELECT * FROM Applications WHERE application_id = :application_id'
    # result = session.execute(sql, {"application_id": application_id})

    result = get_db_connection().execute(sql, {"application_id": application_id}).fetchall()
    # convert the SQL result to a list of dictionaries
    user_data = [dict(row) for row in result]
    #
    # # close the session
    # session.close()

    # return the user data
    return user_data


class Application:
    def __init__(self, application_id):
        self.application_id = application_id

    application_id = db.Column(db.Integer, primary_key=True)
    paid = db.Column(db.Boolean, default=False)
    money_granted = db.Column(db.Float)
    row_number = db.Column(db.Integer, nullable=False)
    sheet_id = db.Column(db.Integer, db.ForeignKey('Spreadsheets.sheet_id'))
