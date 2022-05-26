"""
Flask API handler
run with py api.py

"""

from flask import Flask, request, jsonify
from celeryBroker import saveJson

app = Flask(__name__)


@app.route('/inbound/add_article/<uuid>', methods=['POST'])
def add_article(uuid):
    content = request.json
    saveJson.delay(content)
    return uuid

if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug=True)

