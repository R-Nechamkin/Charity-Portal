from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash

from .database import get_db_connection
from .models import User
from . import db


auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/signup')
def signup():
    return render_template('signup.html')


def manually_check_email(email):
    conn = get_db_connection()
    query = "SELECT * FROM User WHERE email = (?)"
    row = conn.execute(query, (email,)).fetchone()
    conn.close()
    return row


def insert_new_user(username, email, password):
    conn = get_db_connection()
    query = "INSERT INTO User (username, email, password) VALUES (?, ?, ?)"
    conn.execute(query, (username, email, generate_password_hash(password)))
    conn.commit()
    conn.close()

@auth.route('/signup', methods=['POST'])
def signup_post():
    # code to validate and add user to database goes here
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = manually_check_email(email)

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email already registered for different username.')
        return redirect(url_for('auth.login'))

    insert_new_user(name, email, password)

    return redirect(url_for('main.set_up'))


@auth.route('/logout')
def logout():
    return 'Logout'



