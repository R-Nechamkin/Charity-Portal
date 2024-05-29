from typing import List, Set

from sqlalchemy import CheckConstraint
from sqlalchemy.orm import relationship, Mapped
from flask_login import UserMixin


from app import db, create_app, login


@login.user_loader
def load_user(_id):
    return db.session.get(User, int(_id))


class Charity(db.Model):
    __tablename__ = 'Charities'

    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    users = relationship('User', backref='charity')
    fields = relationship('Field', backref='charity')
    records = relationship('Record', backref='charity')


class User(UserMixin, db.Model):
    __tablename__ = 'Users'

    _id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    charity_id = db.Column(db.Integer, db.ForeignKey('Charities.charity_id'), nullable=False)

    def get_id(self):
        return self._id


class Field(db.Model):
    __tablename__ = 'Fields'

    _id = db.Column(db.Integer, primary_key =True)
    name = db.Column(db.String(100), nullable=False)
    data_type = db.Column(db.String(20), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    charity_id = db.Column(db.Integer, db.ForeignKey('Charities.charity_id'), nullable=False)

    charity: Mapped["Charity"] = relationship(back_populates="fields")


class Record(db.Model):
    __tablename__ = 'Records'

    _id = db.Column(db.Integer, primary_key=True)
    charity_id = db.Column(db.Integer, db.ForeignKey('Charities.charity_id'), nullable=False)

    charity: Mapped["Charity"] = relationship(back_populates="records")

    shortText_data: Mapped[Set["ShortTextDatum"]] = relationship(back_populates="record")
    text_data: Mapped[Set["TextDatum"]] = relationship(back_populates="record")
    int_data: Mapped[Set["IntDatum"]] = relationship(back_populates="record")
    numeric_data: Mapped[Set["NumericDatum"]] = relationship(back_populates="record")
    boolean_data: Mapped[Set["BooleanDatum"]] = relationship(back_populates="record")
    date_data: Mapped[Set["DateDatum"]] = relationship(back_populates="record")
    timestamp_data: Mapped[Set["TimestampDatum"]] = relationship(back_populates="record")


class ShortTextDatum(db.Model):
    __tablename__ = 'ShortText_Data'

    _id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(255), nullable=False)

    field_id = db.Column(db.Integer, db.ForeignKey('Fields._id'))
    record_id = db.Column(db.Integer, db.ForeignKey('Records._id'), nullable=False)

    record: Mapped["Record"] = relationship(back_populates="shortText_data")


class TextDatum(db.Model):
    __tablename__ = 'Text_Data'

    _id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Text, nullable=False)

    field_id = db.Column(db.Integer, db.ForeignKey('Fields._id'), nullable=False)
    record_id = db.Column(db.Integer, db.ForeignKey('Records._id'), nullable=False)

    record: Mapped["Record"] = relationship(back_populates="text_data")

class IntDatum(db.Model):
    __tablename__ = 'Int_Data'

    _id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Integer, nullable=False)

    field_id = db.Column(db.Integer, db.ForeignKey('Fields._id'), nullable=False)
    record_id = db.Column(db.Integer, db.ForeignKey('Records._id'), nullable=False)

    record: Mapped["Record"] = relationship(back_populates="int_data")


class NumericDatum(db.Model):
    __tablename__ = 'Numeric_Data'

    _id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Numeric, nullable=False)

    field_id = db.Column(db.Integer, db.ForeignKey('Fields._id'), nullable=False)
    record_id = db.Column(db.Integer, db.ForeignKey('Records._id'), nullable=False)

    record: Mapped["Record"] = relationship(back_populates="numeric_data")


class BooleanDatum(db.Model):
    __tablename__ = 'Boolean_Data'

    _id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Boolean, nullable=False)

    field_id = db.Column(db.Integer, db.ForeignKey('Fields._id'), nullable=False)
    record_id = db.Column(db.Integer, db.ForeignKey('Records._id'), nullable=False)

    record: Mapped["Record"] = relationship(back_populates="boolean_data")


class DateDatum(db.Model):
    __tablename__ = 'Date_Data'

    _id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)

    field_id = db.Column(db.Integer, db.ForeignKey('Fields._id'), nullable=False)
    record_id = db.Column(db.Integer, db.ForeignKey('Records._id'), nullable=False)

    record: Mapped["Record"] = relationship(back_populates="date_data")


class TimestampDatum(db.Model):
    __tablename__ = 'Timestamp_Data'

    _id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, nullable=False)

    field_id = db.Column(db.Integer, db.ForeignKey('Fields._id'), nullable=False)
    record_id = db.Column(db.Integer, db.ForeignKey('Records._id'), nullable=False)

    record: Mapped["Record"] = relationship(back_populates="timestamp_data")


# """Call this once, when you need to create the database
# This might not work"""
# def create_tables():
#     from sqlalchemy import create_engine
#     from .secrets import DB_CONNECTOR
#     from sqlalchemy.orm import sessionmaker, declarative_base
#
#     engine = create_engine(DB_CONNECTOR)
#     Base = declarative_base()
#     Base.metadata.create_all(engine)
#
#     Session = sessionmaker(bind=engine)
#     session = Session()
#
#     print("Tables created successfully.")