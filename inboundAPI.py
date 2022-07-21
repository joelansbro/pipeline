"""
Flask API handler
run with py api.py

"""

from flask import Flask, request, jsonify
from celeryBroker import saveJson, _chainfileprocessing
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


if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug=True)

