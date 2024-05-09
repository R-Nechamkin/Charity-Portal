from flask import jsonify, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from . import db
class User():
    def signup(self):
        user = {
            "_id": uuid.uuid4().hex,
            "username": request.form["name"],
            "email": request.form["email"],
            "password": request.form["password"]

        }

        user['password'] = generate_password_hash(user['password'])

        #check for existing email address
        if db.users.find_one({"email": user['email']}):
            flash('Email already registered for different username.')
            return redirect(url_for('auth.login'))

        if(db.users.insert_one(user)):
            return jsonify(user), 200

        return jsonify({"error": "Signup failed"}), 400
