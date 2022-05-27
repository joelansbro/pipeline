"""
Celery is the task queue, it uses rabbitMQ to handle tasks
for usage, ensure that rabbitMQ is running (see commands text file)

the to start server:
py -m celery --app celeryBroker worker --loglevel=INFO -B

flower is installed to monitor the workflow
py -m celery --app celeryBroker flower

"""

import json
from celery import Celery
from celery.schedules import crontab
# need to figure out how to import intakejob into this script, or move the broker to outside of this folder


app = Celery(
    broker="pyamqp://joel:pipeline@localhost:5672/inbound",
    # this backend stores the queries made
    backend="db+sqlite:///results.sqlite"
)

@app.task
def saveJson(payload, uuid):
    print(type(payload))
    data = json.dumps(payload)
    json_without_slash = json.loads(data)
    with open ('./stash/{}.json'.format(uuid), 'w') as f:
        json.dump(json_without_slash, f)
    return "Saved down file {data}".format(data=data)



@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(10.0, bundle.s(), name='add every 10')

@app.task
def bundle():
    print('This works')