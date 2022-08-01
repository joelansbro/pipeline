# this job can be run separately 
# this job generates reports from the total cleaned scraped data intaken from intakejob and stored in DB
# reports are then also stored within the DB, for access via the outbound API

# business logic layer

# run steps are
# intake - batching - preprocessing - keyword selection - store in SQLite - modelling - prediction/inference
#                                                 our python script is here ^
import sqlite3
from sqlite3 import Error
from DAO import create_connection

report_query = """
SELECT * FROM articles where project = '{}'
"""

def select_report(report):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(report_query.format(report))

    rows = cursor.fetchall()

    for row in rows:
        print(row)

    return str(rows)
    

