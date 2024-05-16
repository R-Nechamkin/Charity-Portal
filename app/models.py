from sqlalchemy.orm import relationship
from flask_login import UserMixin


from app import db, create_app, login


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
    

class Spreadsheet(db.Model):
    __tablename__ = 'Spreadsheets'

    sheet_id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String(255), nullable=False)

    users = relationship('User', backref='spreadsheet')
    # applications = relationship('Application', backref='spreadsheet')
    fields = relationship('Field', backref='spreadsheet')


class User(UserMixin, db.Model):
    __tablename__ = 'Users'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    sheet_id = db.Column(db.Integer, db.ForeignKey('Spreadsheets.sheet_id'))


    def get_id(self):
        return self.user_id
        

# class Application(db.Model):
    # __tablename__ = 'Applications'

    # application_id = db.Column(db.Integer, primary_key=True)
    # paid = db.Column(db.Boolean, default=False)
    # money_granted = db.Column(db.Float)
    # row_number = db.Column(db.Integer, nullable=False)
    # sheet_id = db.Column(db.Integer, db.ForeignKey('Spreadsheets.sheet_id'))


class Field(db.Model):
    __tablename__ = 'Fields'
    
    field_id = db.Column(db.Integer, primary_key =True)
    name = db.Column(db.String(100), nullable=False)
    data_type = db.Column(db.String(20), nullable=False)
    
    sheet_id = db.Column(db.Integer, db.ForeignKey('Spreadsheets.sheet_id'))