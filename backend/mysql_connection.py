import logging
import time

import mysql.connector
from mysql.connector import errorcode
from mysql.connector.connection import MySQLConnection


def ensure_tables_exist(cnx: MySQLConnection):
    cursor = cnx.cursor()
    cursor.execute()


def get_connection(config):
    print(config)
    try:
        cnx = mysql.connector.connect(**config)
        return cnx
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        return None


def get_all_users(cnx: MySQLConnection):
    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:
            cursor.execute("SELECT * FROM user")
            rows = cursor.fetchall()
            for row in rows:
                print(row)
    else:
        print("could not connect")
