import logging
import time

import mysql.connector
from mysql.connector import errorcode


def get_connection(config):
    return mysql.connector.connect(**config)
