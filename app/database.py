import sqlite3

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


