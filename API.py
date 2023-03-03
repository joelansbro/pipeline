"""
Flask API handler

Controls access to the pipeline, ingestion of JSON article data and data requests

Methods:
 - inbound/add_article
 - outbound/get_report/<project>
 - outbound/get_article/<title>
 - test_scheduler

"""

from flask import Flask, request, jsonify
from schema import Schema, And, Use, Optional, SchemaError, Or
import json

from celeryBroker import report_job, saveJson, _chainfileprocessing, result
from DAO import create_connection


app = Flask(__name__)


@app.route('/', methods=['GET'])
def homepage():
    return """
    <h1>Ingestion API</h1>
    <p>This is the API to connect to the pipeline. Please invoke one of the following routes:</p>
    <p>To send an article to the database: 
    inbound/add_article
    </p>
    <p>
    For a single article, if you know the name:
    /outbound/get_article/<article title>
    </p>
    <p>
    For a generic report, post the project name to:
    /outbound/get_report/<project name>
    </p>

    """

@app.route('/inbound/add_article', methods=['POST'])
def add_article():
    """Add an article into the local stash for pipeline processing."""
    
    content = request.json
    parsed = json.dumps(content)
    json_without_slash = json.loads(parsed)
    
    schema_check = check_inbound_schema(json_without_slash)
    
    if schema_check == True:
        saveJson.delay(json_without_slash)
        return 'Saved down JSON'
    
    else:
        return str(schema_check)


@app.route('/outbound/get_report/<project>', methods=['GET'])
def get_report(project: str):
    """Get a report of keywords based upon a job.

    To be fleshed out in future with more jobs, 
    and a method to gain all data in excel format.
    """
    report = report_job.delay(project)

    output = result.AsyncResult(report.id)
    return output.get()


@app.route('/outbound/get_article/<title>', methods=['GET'])
def get_article(title):
    """Gets a single article from the database."""

    response = db_get_article(title)
    return response


@app.route('/test_scheduler', methods=['GET'])
def test_scheduler():
    """Invokes the celery based pipeline manually.
    
    Future running of the pipeline should be scheduled, 
    to continuously accept data.
    """
    response = _chainfileprocessing.delay()
    response = str(response)
    return response

def check_inbound_schema(payload):
    """Checks the received payload to see if it matches the proper format.

    Absolute required fields for the article should be:
    title: string       title of the article
    author: string      author of the article
    project: string     name of the project you are collecting data for. Used to retrieve all data 
                        related to the project so be sure to keep this consistent. 
    content: string     article content, can be any size.
    url: string         location of the actual url of the article page.

    All other fields are optional.
    """
    article_schema = Schema(
    {
        Optional('rowid'):int,
        'title': str,
        'author': str,
        'project': str,
        Optional('date_published'): And(Or(str, int, None)), # check if actual proper date
        Optional('lead_image_url'): And(Or(str, None)),
        'content': str,
        Optional('next_page_url'): And(Or(str, None)),
        'url': str,
        Optional('domain'): And(Or(str, None)),
        Optional('excerpt'): And(Or(str, None)),
        Optional('word_count'): And(Or(int, None)),
        Optional('direction'): And(Or(str, None)),
        Optional('total_pages'): And(Or(int, None)),
        Optional('rendered_pages'): And(Or(int, None))
    }
    )

    try:
        article_schema.validate(payload)
        return True
    except SchemaError as e:
        return 'Schema error found: {}'.format(e)



def db_get_article(title: str):
    """ Retrieve a single article from the database based upon title.
    
    TODO: Retrieve articles via other methods, such as based on author or date. 
    Note: This will require a service such as SQLAlchemy to perform.
    """

    article_query = """SELECT * FROM articles where title = '{_title}' LIMIT 1;"""
    cursor = create_connection()
    title = title.replace("%20", " ")
    response = cursor.execute(article_query.format(_title=title)).fetchone()
    print("Jobs a goodn")
    return jsonify(response)

if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug=True)
