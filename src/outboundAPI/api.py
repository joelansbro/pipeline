# the outbound module dictates an API that interacts with a front end service 
# this api desginates endpoints for interacting with the database to pull report data through

# contains code that implements the user interface


import json

from flask import Flask
from ...src.databaseConn.DAO import Session, engine, fetch_single_article

app = Flask(__name__)

@app.route('/article/<uuid>')
def get_article(uuid):
    article = fetch_single_article(engine, uuid)
    return json.dumps(article)


if __name__ == '__main__':
    app.run()



# have the API accomplish two things

# 1) get individual articles based on specific project and article title - over to a basic frontend
# 2) send an API to build a Python job in the events queue that will create generic reports from the article data