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
    return "post JSON to endpoint localhost/inbound/add_article/uniqueID"

@app.route('/inbound/add_article', methods=['POST'])
def add_article():
    content = request.json
    parsed = json.dumps(content)
    json_without_slash = json.loads(parsed)
    schema_check = check_inbound_schema(json_without_slash)
    if schema_check:
        saveJson.delay(json_without_slash)
        return 'Saved down JSON'
    else:
        return schema_check

@app.route('/test_scheduler', methods=['GET'])
def test_scheduler():
    response = _chainfileprocessing.delay()
    response = str(response)
    return response


def check_inbound_schema(payload):
    article_schema = Schema(
    {
        'title': str,
        'author': str,
        'project': str,
        Optional('date_published'): And(Or(str, int)), # check if actual proper date
        Optional('lead_image_url'): str,
        'content': str,
        Optional('next_page_url'): str,
        'url': str,
        Optional('domain'): str,
        Optional('excerpt'): str,
        Optional('word_count'): int,
        Optional('direction'): str,
        Optional('total_pages'): int,
        Optional('rendered_pages'): int
    }
    )
    try:
        article_schema.validate(payload)
        return True
    except SchemaError as e:
        return 'Schema error found: {}'.format(e)

if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug=True)
