from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text, CheckConstraint
from sqlalchemy.dialects.mssql.information_schema import columns
from sqlalchemy.sql import text
from .secrets import DB_CONNECTOR
from . import db
from .models import *


def get_sql_type(field_type):
    dictionary = {"SHORT_TEXT": db.String(255), "INT": db.Integer,
            "DECIMAL": db.Decimal, "BOOLEAN": db.Boolean,
            "DATE": db.Date, "TEXT": db.Text, "TIMESTAMP": db.DateTime,
                  "EMAIL": db.Email}

    return dictionary[field_type.upper()]


def insert_fields_into_table(field_details, charity_id):
    for field_name, field_type, field_num in field_details:
        new_field = Field(name=field_name, data_type=field_type, order=field_num, charity_id=charity_id)
        db.session.add(new_field)


def get_last_id(table_name):
    engine = create_engine(DB_CONNECTOR)
    query = 'select LAST_INSERT_ID() from ' + table_name
    return engine.execute(query).fetchone()



def create_table(field_details, user):
    insert_fields_into_table(field_details, user.charity_id)
    db.session.commit()


def insert_datum(datum, record, field):
    if field.data_type == 'SHORT_TEXT':
        return ShortTextDatum(datum=datum, record=record, field=field)
    elif field.data_type == 'TEXT':
        return TextDatum(datum=datum, record=record, field=field)
    elif field.data_type == 'INT':
        return IntDatum(datum=datum, record=record, field=field)
    elif field.data_type == 'DECIMAL':
        return DecimalDatum(datum=datum, record=record, field=field)
    elif field.data_type == 'BOOLEAN':
        return BooleanDatum(datum=datum, record=record, field=field)
    elif field.data_type == 'DATE':
        return DateDatum(datum=datum, record=record, field=field)
    elif field.data_type == 'TIMESTAMP':
        return TimestampDatum(datum=datum, record=record, field=field)
    elif field.data_type == 'EMAIL':
        return EmailDatum(datum=datum, record=record, field=field)
    else:
        raise Exception('Field type has no corresponding table')


def internal_insert_user_data(charity, data, headers, records):
    for header in headers:
        field=Field.query.filter_by(name=header).one()
        for datum, record in data, records:
            try:
                datum=insert_datum(datum=datum, record=record, field=field)
            except Exception as e:
                raise Exception('Database error occured while inserting data') from e
            db.session.add(datum)


def insert_user_data(charity, data, headers):
    try:
        records = []
        for _ in data:
            record = Record(charity=charity)
            db.session.add(record)
            records.append(record)

        internal_insert_user_data(charity=charity, data=data, headers=headers, records=records)

        db.session.commit()
    except Exception as e:
        raise Exception('Database error occured while inserting data') from e


from sqlalchemy import create_engine, DDL


# TODO remember to call this before publishing the website
def create_email_format_function():
    engine = create_engine(DB_CONNECTOR)
    email_format_function = DDL("""
        CREATE FUNCTION email_format(email VARCHAR(255)) RETURNS BOOLEAN
        BEGIN
            DECLARE pattern VARCHAR(255);
            SET pattern = '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$';
            RETURN email REGEXP pattern;
        END
    """)
    engine.execute(email_format_function)
