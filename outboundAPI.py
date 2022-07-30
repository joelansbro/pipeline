# Flask app to query a single article from ./data/maindb.sqlite

from flask import Flask, jsonify
from celeryBroker import saveJson, _chainfileprocessing
from config import SQLITE_DATABASE
import time
import sqlite3
import json
import subprocess

app = Flask(__name__)


@app.route('/', methods=['GET'])
def homepage():
    return """
    <h1>OutboundAPI</h1>
    <p>
    Hello! You have visited the outbound API!</p>
    <p>
    Instead of visiting this link, you will want to post a GET request to the following paths:</p>
    <p>
    For a single article, if you know the name:
    /outbound/get_article/<article title></p>
    <p>
    For a generic report, post the project name to:
    /outbound/get_report/<project name></p>

    """

@app.route('/outbound/get_article/<title>', methods=['GET'])
def get_article(title):
    response = db_get_article(title)
    return response


def db_get_article(title: str):
    sqliteConnection = sqlite3.connect(SQLITE_DATABASE)
    cursor = sqliteConnection.cursor()
    title = title.replace("%20", " ")
    print("Connected to SQLite")
    response = cursor.execute(article_query.format(_title=title)).fetchone()
    print("Jobs a goodn")
    return jsonify(response)

article_query = """SELECT * FROM articles where title = '{_title}' LIMIT 1;"""



if __name__ == '__main__':
    app.run(host = '0.0.0.0', port=5050, debug=True)