from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text
from sqlalchemy.sql import text
from .secrets import DB_CONNECTOR
from . import db


def create_data_table(table_name, field_details):
    metadata = MetaData()
    fields = []
    for field_name, field_type in field_details:
        if field_type == 'Email':
            fields.append(Column(field_name, String(255), nullable=False))
            constraint = CheckConstraint(f"email_format({field_name})", name=f"chk_{field_name}_email_format")
            columns.append(Column(field_name, column_type, constraint=constraint))

        else:
            fields.append(Column(field_name, field_type))
    table = Table(table_name, metadata, *fields)
    metadata.create_all(db.engine)
    
    
def insert_fields_into_table(field_details, sheet_id):
    for field_name, field_type in field_details:
        new_field = Field(name = field_name, data_type = field_type, sheet_id = sheet_id)
        db.session.add(new_field)


def get_last_id(table_name):
    engine = create_engine(DB_CONNECTOR)
    query = 'select LAST_INSERT_ID() from ' + table_name
    return query.execute()


    
def create_spreadsheet_record(user, table_name):
    new_sheet = Spreadsheet(table_name = table_name)
    db.session.add(new_sheet)
    
    sheet_id = get_last_id('Spreadsheets')
    user.sheet_id = sheet_id
    return sheet_id
    

def create_table(table_name, field_details, current_user):
    create_data_table(table_name, field_details)
    sheet_id = create_spreadsheet_record(current_user, table_name)
    insert_fields_into_table(field_details, sheet_id)
    db.session.commit()


  

from sqlalchemy import create_engine, DDL
#TODO remember to call this before publishing the website
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



