import logging
import time

import mysql.connector
from config import config
from mysql.connector import errorcode


def get_connection():
    return mysql.connector.connect(**config)
