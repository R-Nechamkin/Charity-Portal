import sqlite3

from app import create_app, db


def set_up_database():
    connection = sqlite3.connect('testdb.sqlite')
    with open('testdb.sql') as f:
        connection.executescript(f.read())


def get_db_connection():
    conn = sqlite3.connect('testdb.sqlite')
    conn.row_factory = sqlite3.Row
    return conn


def get_stuff_from_db():
    conn = get_db_connection()
    return conn.execute('SELECT * FROM Users').fetchall()


def get_url_by_user_id(user_id):
    conn = get_db_connection()
    query = """
        SELECT url FROM Spreadsheets
        JOIN Users ON Spreadsheets.sheet_id = Users.sheet_id
        WHERE user_id = (?)"""

    result = conn.execute(query, (user_id, )).fetchone()
    return result[0]


def get_latest_pk_of_spreadsheet():
    conn = get_db_connection()
    query = 'SELECT MAX(sheet_id) AS sheet_id from Spreadsheets'
    return conn.execute(query).fetchone()['sheet_id']




def get_all_data_from_table(table_name):
    conn = get_db_connection()
    query = 'SELECT * FROM {}'.format(table_name)
    return conn.execute(query).fetchall()

def add_a_user_to_db():
    conn = get_db_connection()
    query = """INSERT INTO Users (username, password, email) VALUES ('User 1', 'password1', 'email1@example.com')"""
    conn.execute(query)
    conn.commit()
    conn.close()


def get_some_data():
    conn = get_db_connection()
    user_id = 1;

    query = """
     SELECT url FROM User
             JOIN Spreadsheet ON Spreadsheet.sheet_id = User.sheet_id
             Where User.user_id = (?)"""

    result = conn.execute(query, (user_id,))
    return result
