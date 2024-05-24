from sqlalchemy import CheckConstraint
from sqlalchemy.orm import relationship
from flask_login import UserMixin


from app import db, create_app, login


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
    

class Charity(db.Model):
    __tablename__ = 'Charities'

    charity_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    users = relationship('User', backref='charity')
    # applications = relationship('Application', backref='charity')
    fields = relationship('Field', backref='charity')
    records = relationship('Record', backref='charity')


class User(UserMixin, db.Model):
    __tablename__ = 'Users'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    charity_id = db.Column(db.Integer, db.ForeignKey('Charities.charity_id'), nullable=False)


    def get_id(self):
        return self.user_id
        


class Field(db.Model):
    __tablename__ = 'Fields'
    
    field_id = db.Column(db.Integer, primary_key =True)
    name = db.Column(db.String(100), nullable=False)
    data_type = db.Column(db.String(20), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    
    charity_id = db.Column(db.Integer, db.ForeignKey('Charities.charity_id'))
    
    
class Record(db.Model):
    __tablename__ = 'Records'

    record_id = db.Column(db.Integer, primary_key=True)
    charity_id = db.Column(db.Integer, db.ForeignKey('Charities.charity_id'))

    shortText_data = relationship('ShortTextDatum', backref='record')
    int_data = relationship('IntDatum', backref='record')
    decimal_data = relationship('DecimalDatum', backref='record')
    boolean_data = relationship('BooleanDatum', backref='record')
    date_data = relationship('DateDatum', backref='record')
    text_data = relationship('TextDatum', backref='record')
    timestamp_data = relationship('TimestampDatum', backref='record')

 
class ShortTextDatum(db.Model):
    __tablename__ = 'ShortText_Data'

    data_id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(255), nullable=False)
    
    field_id = db.Column(db.Integer, db.ForeignKey('Fields.field_id'))
    record_id = db.Column(db.Integer, db.ForeignKey('Records.record_id'), nullable=False)


class IntDatum(db.Model):
    __tablename__ = 'Int_Data'

    data_id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Integer, nullable=False)
    
    field_id = db.Column(db.Integer, db.ForeignKey('Fields.field_id'), nullable=False)
    record_id = db.Column(db.Integer, db.ForeignKey('Records.record_id'), nullable=False)


#TODO: Rename to NumericDatum
class DecimalDatum(db.Model):
    __tablename__ = 'Decimal_Data'

    data_id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Numeric, nullable=False)
    
    field_id = db.Column(db.Integer, db.ForeignKey('Fields.field_id'), nullable=False)
    record_id = db.Column(db.Integer, db.ForeignKey('Records.record_id'), nullable=False)
    
    
class CurrencyDatum(db.Model):
    __tablename__ = 'Currency_Data'

    data_id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Numeric, nullable=False)
    
    field_id = db.Column(db.Integer, db.ForeignKey('Fields.field_id'), nullable=False)
    record_id = db.Column(db.Integer, db.ForeignKey('Records.record_id'), nullable=False)


class BooleanDatum(db.Model):
    __tablename__ = 'Boolean_Data'

    data_id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Boolean, nullable=False)
    
    field_id = db.Column(db.Integer, db.ForeignKey('Fields.field_id'), nullable=False)
    record_id = db.Column(db.Integer, db.ForeignKey('Records.record_id'), nullable=False)


class DateDatum(db.Model):
    __tablename__ = 'Date_Data'

    data_id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    
    field_id = db.Column(db.Integer, db.ForeignKey('Fields.field_id'), nullable=False)
    record_id = db.Column(db.Integer, db.ForeignKey('Records.record_id'), nullable=False)


class TextDatum(db.Model):
    __tablename__ = 'Text_Data'

    data_id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Text, nullable=False)
    
    field_id = db.Column(db.Integer, db.ForeignKey('Fields.field_id'), nullable=False)
    record_id = db.Column(db.Integer, db.ForeignKey('Records.record_id'), nullable=False)


class TimestampDatum(db.Model):
    __tablename__ = 'Timestamp_Data'

    data_id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, nullable=False)

    field_id = db.Column(db.Integer, db.ForeignKey('Fields.field_id'), nullable=False)
    record_id = db.Column(db.Integer, db.ForeignKey('Records.record_id'), nullable=False)


class EmailDatum(db.Model):
    __tablename__ = 'Email_Data'

    data_id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Text, nullable=False)

    field_id = db.Column(db.Integer, db.ForeignKey('Fields.field_id'), nullable=False)
    record_id = db.Column(db.Integer, db.ForeignKey('Records.record_id'), nullable=False)

    #TODO: create the constraint for email formatting
    #constraint = CheckConstraint(sqltext="", name="email_format")
