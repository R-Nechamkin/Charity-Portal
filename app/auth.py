from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash

from .database import get_db_connection
from .models import User
from . import db


auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    # login code
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials

    return redirect(url_for('main.profile'))

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
    # code to validate and add user to database
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



