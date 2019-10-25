import sqlite3
import sys
import os
from .. import constants as const

def get_connection():
    return sqlite3.connect(const.DB_NAME)

def execute(sql_statement, statement_args=None, commit=False, fetch=False):
    conn = get_connection()
    cursor = conn.cursor()
    ret = None

    if statement_args:
        cursor.execute(sql_statement, statement_args)
    else:
        cursor.execute(sql_statement)
    if fetch:
        ret = cursor.fetchall()
    cursor.close()
    if commit:
        conn.commit()
    conn.close()
    return ret

def create_db():
    execute(const.CREATE_USER_LOG_TABLE, commit=True)

def insert_log_entry(user_id, tournament_id, score, waves, log):
    execute(const.INSERT_SINGLE_LOG_TABLE, (user_id, tournament_id, score, waves, log), commit=True)

def select_log_entry(user_id, tournament_id):
    entry = None
    records = execute(const.SELECT_LOG_TABLE_BY_USER_AND_TOURNAMENT, (user_id, tournament_id), fetch=True)
    if records:
        if len(records) > 0:
            entry = records[0]

    return entry

def update_log_entry(user_id, tournament_id, score, waves, log):
    execute(const.UPDATE_LOG_TABLE_FOR_USER_AND_TOURNAMENT, (score, waves, log, user_id, tournament_id), commit=True)


#Create the db and user logs table if it doesn't exist
if (not os.path.isfile(const.DB_NAME)):
    create_db()

