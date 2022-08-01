# main file to create the sqlite connection
import sqlite3
from sqlite3 import Error
from config import SQLITE_DATABASE

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(SQLITE_DATABASE)
    except Error as e:
        print(e)

    return conn
