"""
Celery is the task queue, it uses rabbitMQ to handle tasks
for usage, ensure that rabbitMQ is running (see commands text file)

the to start server:
py -m celery --app celeryBroker worker --loglevel=INFO

flower is installed to monitor the workflow
ry -m celery --app celeryBroker flower

"""
import json
from celery import Celery

app = Celery(
    broker="pyamqp://joel:pipeline@localhost:5672/inbound",
    # this backend stores the queries made
    backend="db+sqlite:///results.sqlite"
)

@app.task
def saveJson(payload):
    print(type(payload))
    data = json.dumps(payload)
    with open ('data.json', 'w') as f:
        json.dump(data, f)
    print(data)
    return "Saved down file {data}".format(data=data)