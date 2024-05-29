import numbers

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text, CheckConstraint
from sqlalchemy.dialects.mssql.information_schema import columns
from sqlalchemy.sql import text
from .secrets import DB_CONNECTOR
from . import db
from .models import *


def get_sql_type(field_type):
    dictionary = {"SHORT_TEXT": ShortTextDatum, "INT": IntDatum,
                  "DECIMAL": NumericDatum, "BOOLEAN": BooleanDatum,
                  "DATE": DateDatum, "TEXT": TextDatum, "TIMESTAMP": TimestampDatum,
                  "EMAIL": EmailDatum, "CURRENCY": CurrencyDatum}

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


def insert_datum(datum, record_id, field):
    if field.data_type == 'SHORT_TEXT':
        return ShortTextDatum(data=datum, record_id=record_id, field_id=field.field_id)
    elif field.data_type == 'TEXT':
        return TextDatum(data=datum, record_id=record_id, field_id=field.field_id)
    elif field.data_type == 'INT':
        return IntDatum(data=datum, record_id=record_id, field_id=field.field_id)
    elif field.data_type == 'DECIMAL':
        if isinstance(datum, str):
            datum = datum.replace('.', '').replace(',', '')
        return NumericDatum(data=datum, record_id=record_id, field_id=field.field_id)
    elif field.data_type == 'CURRENCY':
        if isinstance(datum, str):
            datum = datum.replace('.', '').replace(',', '').replace('$', '')
        return NumericDatum(data=datum, record_id=record_id, field_id=field.field_id)
    elif field.data_type == 'BOOLEAN':
        return BooleanDatum(data=datum, record_id=record_id, field_id=field.field_id)
    elif field.data_type == 'DATE':
        return DateDatum(data=datum, record_id=record_id, field_id=field.field_id)
    elif field.data_type == 'TIMESTAMP':
        return TimestampDatum(data=datum, record_id=record_id, field_id=field.field_id)
    elif field.data_type == 'EMAIL':
        return EmailDatum(data=datum, record_id=record_id, field_id=field.field_id)
    else:
        raise Exception('Field type has no corresponding table')


def get_datum(record, field):
    r = record.record_id
    f = field.field_id
    row = (db.session.query(ShortTextDatum).filter_by(record_id=r, field_id=f)
           .union(db.session.query(IntDatum).filter_by(record_id=r, field_id=f))
           .union(db.session.query(NumericDatum).filter_by(record_id=r, field_id=f))
           .union(db.session.query(DateDatum).filter_by(record_id=r, field_id=f))
           .union(db.session.query(BooleanDatum).filter_by(record_id=r, field_id=f))
           .union(db.session.query(EmailDatum).filter_by(record_id=r, field_id=f))
           .union(db.session.query(TimestampDatum).filter_by(record_id=r, field_id=f))
           .union(db.session.query(TextDatum).filter_by(record_id=r, field_id=f))
           ).first()

    if row is None:
        return "___"
    return row.data


def internal_insert_user_data(data, headers, records):
    for i in range(len(headers)):
        field = headers[i]
        for j in range(len(records)):
            try:
                datum = insert_datum(datum=data[j][i], record_id=records[j].record_id, field=field)
            except Exception as e:
                raise Exception('Database error occured while inserting data') from e
            db.session.add(datum)


def delete_record_and_commit(record_id):
    ShortTextDatum.query.filter_by(record_id=record_id).delete()
    IntDatum.query.filter_by(record_id=record_id).delete()
    NumericDatum.query.filter_by(record_id=record_id).delete()
    DateDatum.query.filter_by(record_id=record_id).delete()
    BooleanDatum.query.filter_by(record_id=record_id).delete()
    EmailDatum.query.filter_by(record_id=record_id).delete()
    TimestampDatum.query.filter_by(record_id=record_id).delete()
    TextDatum.query.filter_by(record_id=record_id).delete()

    db.session.commit()

    Record.query.filter_by(record_id=record_id).delete()
    db.session.commit()


def insert_user_data(charity, data, headers):
    records = []
    try:
        for _ in data:
            record = Record(charity=charity)
            db.session.add(record)
            records.append(record)

        db.session.commit()

        internal_insert_user_data(data=data, headers=headers, records=records)

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        for r in records:
            delete_record_and_commit(r.record_id)
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
