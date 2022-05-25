"""
Flask API handler
run with py api.py

"""

from flask import Flask, request, jsonify
from celeryBroker import printResponse

app = Flask(__name__)

@app.route('/inboundapi/add_message/<uuid>', methods=['POST'])
def add_message(uuid):
    content = request.json
    # print(content['mytext'])
    return printResponse.delay(content)
    # return jsonify({"uuid":uuid})


if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug=True)

