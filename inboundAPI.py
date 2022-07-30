"""
Flask API handler
run with py api.py

"""

from flask import Flask, request, jsonify
from celeryBroker import saveJson, _chainfileprocessing
from schema import Schema, And, Use, Optional, SchemaError, Or
import json

app = Flask(__name__)


@app.route('/', methods=['GET'])
def homepage():
    return """
    InboundAPI
    Hello! You have directed yourself via the browser to the inbound page!
    You cannot (yet) use this page to submit articles for manipulation.
    Instead, you must POST your data to the endpoint:
    /inbound/add_article
    """

@app.route('/inbound/add_article', methods=['POST'])
def add_article():
    content = request.json
    parsed = json.dumps(content)
    json_without_slash = json.loads(parsed)
    schema_check = check_inbound_schema(json_without_slash)
    if schema_check == True:
        saveJson.delay(json_without_slash)
        return 'Saved down JSON'
    else:
        return str(schema_check)

@app.route('/test_scheduler', methods=['GET'])
def test_scheduler():
    response = _chainfileprocessing.delay()
    response = str(response)
    return response


def check_inbound_schema(payload):
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

if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug=True)
