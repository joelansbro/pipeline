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

@app.route('/inbound/add_article/<uuid>', methods=['POST'])
def add_article(uuid):
    content = request.json
    parsed = json.dumps(content)
    json_without_slash = json.loads(parsed)
    saveJson.delay(json_without_slash, uuid)
    return uuid

@app.route('/test_scheduler', methods=['GET'])
def test_scheduler():
    response = _chainfileprocessing.delay()
    response = str(response)
    return response



@app.route('/check_inbound_schema', methods=['GET'])
def check_inbound_schema():
    # article_schema = Schema(
    # {
    #     'title': str,
    #     'author': str,
    #     'project': str,
    #     Optional('date_published'): And(Or(str, int)),
    #     Optional('lead_image_url'): str,
    #     'content': str,
    #     Optional('next_page_url'): str,
    #     'url': str,
    #     Optional('domain'): str,
    #     Optional('excerpt'): str,
    #     Optional('word_count'): int,
    #     Optional('direction'): str,
    #     Optional('total_pages'): int,
    #     Optional('rendered_pages'): int
    # }
    # )
    article_schema = Schema(
        {'title':str,
        'author':str,
        'project':str,
        'content':str,
        'url':str
    })
    test_data = {
        'title':'test-title',
        'author':'test-author',
        'project':'test-project',
        'content':'test-content',
    } 
    try:
        test_validation = article_schema.validate(test_data)
        return 'All good here'
    except SchemaError:
        return "Schema error within data"


if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug=True)
