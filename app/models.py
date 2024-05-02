# This code came straight from chatgpt so hopefully it's correct

from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, ForeignKey, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Spreadsheet(Base):
    __tablename__ = 'Spreadsheet'

    sheet_id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)

    users = relationship('User', backref='spreadsheet')
    applications = relationship('Application', backref='spreadsheet')


class User(Base):
    __tablename__ = 'User'

    user_id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False)
    sheet_id = Column(Integer, ForeignKey('Spreadsheet.sheet_id'))


class Application(Base):
    __tablename__ = 'Application'

    application_id = Column(Integer, primary_key=True)
    paid = Column(Boolean, default=False)
    money_granted = Column(Float)
    row_number = Column(Integer, nullable=False)
    sheet_id = Column(Integer, ForeignKey('Spreadsheet.sheet_id'))

engine = create_engine('sqlite:///testdb.db')
Base.metadata.create_all(engine)
