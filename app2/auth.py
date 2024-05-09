from flask import Flask, render_template

from app2.models import User
import pymongo

app = Flask(__name__)

#database

@app.route('/signup')
def signup_page():
    return render_template('signup.html')


@app.route('/signup', methods=['POST'])
def signup():
    return User().signup()
