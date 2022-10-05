# this job can be run separately 
# this job generates reports from the total cleaned scraped data intaken from intakejob and stored in DB
# reports are then also stored within the DB, for access via the outbound API

# business logic layer

# run steps are
# intake - batching - preprocessing - keyword selection - store in SQLite - modelling - prediction/inference
#                                                 our python script is here ^
from DAO import create_connection

report_query = """
SELECT keywords FROM articles where project = '{}'
"""

def select_report(report):
    """
    This is a very basic report that is returned - it searches through the keywords 
    between all articles in the reports and returns the twenty most common keywords
    in all reports.

    A very basic task to demonstrate the MVP of the pipeline
    """
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(report_query.format(report))

    rows = cursor.fetchall()

    keyword_list = []
    for row in rows:
        keywords = row[0].split(",")
        for key in keywords:
            keyword_list.append(key)

    frequency_dict = {i:keyword_list.count(i) for i in keyword_list}
    twenty_most_common = sorted(frequency_dict, key=frequency_dict.get, reverse=True)[:20]
    most_common = sorted(frequency_dict, key=frequency_dict.get, reverse=True)

    return most_common