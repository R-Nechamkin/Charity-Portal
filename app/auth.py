# auth.py

from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_user, logout_user, login_required
from .models import User, Spreadsheet
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if user actually exists
    # take the user supplied password, hash it, and compare it to the hashed password in database
    if not user or not check_password_hash(user.password, password): 
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():

    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    # sheet_url = request.form.get('sheet_url')

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again  
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))
    
    pattern = r'^[a-zA-Z0-9]+$'
    # We use the username in a lot of random places, so for simplicity's sake, let's require it to be simple
    if bool(re.match(pattern, s)) and ' ' not in s:
        flash('Username must be alphanumeric and cannot contain spaces.')

    # #create spreadsheet in database
    # sheet = Spreadsheet.query.filter_by(url=sheet_url).first() # if this returns a user, then the sheet already exists in database
    # if not sheet:
        # sheet = Spreadsheet(url = sheet_url)
        # db.session.add(sheet)
        # db.session.commit()

    # create new user with the form data. Hash the password so plaintext version isn't saved.
    new_user = User(email=email, username=name, password=generate_password_hash(password), sheet_id = sheet.sheet_id)


    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))