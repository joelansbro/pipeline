# pipeline
 API Pipeline DB middleware


This repository forms the backbone pipeline of the application, forming the pipeline between Extracting Transforming and Loading of the scraped data.

This path includes:
- REST API Methods to intake new data from an external scraping application
- REST API to query data in the form of raw data and processed reports to pass onto a front0end
- Connection to store the processed reports externally in a database
- Data cleaning jobs that clean through the data prior to storage within the Database
- Automation scripts to arrange the jobs

Unsure of what language to write in, 

Presentation Layer - inboundAPI and outboundAPI
Business Logic Layer - processing > intakejob and reportjob
Persistence Layer - databaseConn > DAO

-----

runjob.py should start all related servers with their ports
currently starts Flask api

`py -m celery --app celeryBroker worker --loglevel=INFO -B -s ./data/beat.schedule`

Flask 

The inboundAPI is now currently activated via runjob.py within root, which triggers api.py:

`py runjob.py`

In the end we will want a full script (perhaps a shell script) that activates all servers and ports

Test script 

`py inboundAPI/testapi.py`

TODO: Use marshmallow for json schema validation and serialisation

-----





Python 3.10
Flask - micro web framework for REST API
PySpark - multithreaded data processing
Pandas - Data manipulation
Numpy - for graphing
matplotlib - graphing
RabbitMQ - message broker - likely requires erlang to be installed also
Celery - task management framework asynchronous task queue + scheduling
SQLalchemy - for creating
SpaCY for NLP jobs

just putting this here for reference in the future