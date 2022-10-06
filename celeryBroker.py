"""
Celery is the task queue, it uses rabbitMQ to handle tasks
for usage, ensure that rabbitMQ is running (see commands text file)

the to start server:
py -m celery --app celeryBroker worker --loglevel=INFO -B -s ./data/beat.schedule

flower is installed to monitor the workflow
py -m celery --app celeryBroker flower

"""

import json
from celery import Celery, chain, result
from celery.schedules import crontab
from config import CELERY_BROKER, CELERY_BACKEND
import intakejob, cleanjob, keywordjob, reportjob
from pipe_utils import parquet_name

broker = Celery(
    broker=CELERY_BROKER,
    # this backend stores the queries made
    backend=CELERY_BACKEND
)

@broker.task
def saveJson(payload):
    print(type(payload))
    data = json.dumps(payload)
    json_without_slash = json.loads(data)
    filename = parquet_name()
    with open ('./data/stash/{}.json'.format(filename), 'w') as f:
        json.dump(json_without_slash, f)
    return "Saved down file {}".format(filename)

@broker.task
def report_job(report):
    print('sent to celery')
    response = reportjob.select_report(report)
    return response

# This and bundle() to test scheduling
@broker.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(10.0, bundle.s(), name='add every 10')

@broker.task
def bundle():
    print("Bump")

# Pipeline Entry Call - want to eventually set this onto an hour schedule for instance
@broker.task
def _chainfileprocessing():
    response = chain( 
        intakejob.intakejob(),
        cleanjob.cleanjob(),
        keywordjob.keywordjob()
        ).apply_async()
    return response