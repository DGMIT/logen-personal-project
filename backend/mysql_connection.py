import logging
import time

import mysql.connector
from mysql.connector import errorcode
from mysql.connector.connection import MySQLConnection


def get_connection(config):
    return mysql.connector.connect(**config)


def get_all_users(cnx: MySQLConnection):
    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:
            cursor.execute("SELECT * FROM user")
            rows = cursor.fetchall()
            for row in rows:
                print(row)
        cnx.close()
    else:
        print("could not connect")
