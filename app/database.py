import numbers
import re

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text, CheckConstraint
from sqlalchemy.dialects.mssql.information_schema import columns
from sqlalchemy.sql import text
from .secrets import DB_CONNECTOR
from . import db
from .models import *
from .util import check_email_format


def get_field_names(charity_id: int) -> list:
    return db.session.query(Field.name).filter(Field.charity_id == charity_id).all()


dataTypes = {"SHORT_TEXT": ShortTextDatum, "INT": IntDatum,
              "DECIMAL": NumericDatum, "BOOLEAN": BooleanDatum,
              "DATE": DateDatum, "TEXT": TextDatum, "TIMESTAMP": TimestampDatum,
              "EMAIL": ShortTextDatum, "CURRENCY": NumericDatum}
def get_sql_type(field_type):
    return dataTypes[field_type.upper()]


def insert_fields_into_table(field_details, charity_id):
    for field_name, field_type, field_num in field_details:
        new_field = Field(name=field_name, data_type=field_type, order=field_num, charity_id=charity_id)
        db.session.add(new_field)


def get_last_id(table_name):
    engine = create_engine(DB_CONNECTOR)
    query = 'select LAST_INSERT_ID() from ' + table_name
    return engine.execute(query).fetchone()


def create_table(field_details, user):
    insert_fields_into_table(field_details, user._id)
    db.session.commit()


def insert_datum(datum, record_id, field):
    print(field)
    if field.data_type == 'SHORT_TEXT':
        return ShortTextDatum(data=datum, record_id=record_id, field_id=field._id)
    elif field.data_type == 'TEXT':
        return TextDatum(data=datum, record_id=record_id, field_id=field._id)
    elif field.data_type == 'INT':
        return IntDatum(data=datum, record_id=record_id, field_id=field._id)
    elif field.data_type == 'DECIMAL':
        if isinstance(datum, str):
            datum = datum.replace(',', '')
        return NumericDatum(data=datum, record_id=record_id, field_id=field._id)
    elif field.data_type == 'CURRENCY':
        if isinstance(datum, str):
            datum = datum.replace(',', '').replace('$', '')
        return NumericDatum(data=datum, record_id=record_id, field_id=field._id)
    elif field.data_type == 'BOOLEAN':
        return BooleanDatum(data=datum, record_id=record_id, field_id=field._id)
    elif field.data_type == 'DATE':
        return DateDatum(data=datum, record_id=record_id, field_id=field._id)
    elif field.data_type == 'TIMESTAMP':
        return TimestampDatum(data=datum, record_id=record_id, field_id=field._id)
    elif field.data_type == 'EMAIL':
        if not check_email_format(datum):
            raise Exception('Expected text to match email data type, but was instead: ' + datum)
        return ShortTextDatum(data=datum, record_id=record_id, field_id=field._id)
    else:
        raise Exception('Field type has no corresponding table')


def get_datum(record, field):
    r = record._id
    f = field._id
    row = (db.session.query(ShortTextDatum).filter_by(record_id=r, field_id=f)
           .union(db.session.query(IntDatum).filter_by(record_id=r, field_id=f))
           .union(db.session.query(NumericDatum).filter_by(record_id=r, field_id=f))
           .union(db.session.query(DateDatum).filter_by(record_id=r, field_id=f))
           .union(db.session.query(BooleanDatum).filter_by(record_id=r, field_id=f))
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
                datum = insert_datum(datum=data[j][i], record_id=records[j]._id, field=field)
            except Exception as e:
                raise Exception('Database error occured while inserting data') from e
            db.session.add(datum)


def delete_record_and_commit(record_id):
    ShortTextDatum.query.filter_by(_id=record_id).delete()
    IntDatum.query.filter_by(_id=record_id).delete()
    NumericDatum.query.filter_by(_id=record_id).delete()
    DateDatum.query.filter_by(_id=record_id).delete()
    BooleanDatum.query.filter_by(_id=record_id).delete()
    TimestampDatum.query.filter_by(_id=record_id).delete()
    TextDatum.query.filter_by(_id=record_id).delete()

    db.session.commit()

    Record.query.filter_by(_id=record_id).delete()
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
            delete_record_and_commit(r._id)
        raise Exception('Database error occured while inserting data') from e


from sqlalchemy import create_engine, DDL


