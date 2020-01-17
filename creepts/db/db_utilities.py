import sqlite3
import sys
import os
import logging
from .. import constants as const

LOGGER = logging

def get_connection():
    return sqlite3.connect(const.DB_NAME)

def execute(sql_statement, statement_args=None, commit=False, fetch=False):
    conn = get_connection()
    conn.set_trace_callback(LOGGER.debug)
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
    LOGGER.info("Creating database %s", const.DB_NAME)
    execute(const.CREATE_USER_LOG_TABLE, commit=True)

def insert_log_entry(user_id, tournament_id, score, waves, log):
    execute(const.INSERT_SINGLE_LOG_TABLE, (user_id, tournament_id, score, waves, log), commit=True)

def select_log_entry(user_id, tournament_id):
    entry = None
    records = execute(const.SELECT_LOG_TABLE_FROM_USER_AND_TOURNAMENT, (user_id, tournament_id), fetch=True)
    if records:
        if len(records) > 0:
            entry = records[0]

    return entry

def select_log_entries_from_tournaments(tournament_ids):
    #Transform all given ids in strings and join them in a single string separated by commas
    tournament_ids_formatted = ", ".join(["'{}'".format(t) for t in tournament_ids])
    tournament_ids_formatted = "({})".format(tournament_ids_formatted)
    return execute(const.BASE_SELECT_LOG_TABLE_FROM_TOURNAMENTS + tournament_ids_formatted, fetch=True)

def update_log_entry(user_id, tournament_id, score, waves, log):
    execute(const.UPDATE_LOG_TABLE_FOR_USER_AND_TOURNAMENT, (score, waves, log, user_id, tournament_id), commit=True)

#Create the db and user logs table if it doesn't exist
if (not os.path.isfile(const.DB_NAME)):
    create_db()

