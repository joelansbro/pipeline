# pipeline
 API Pipeline DB middleware


This repository forms the backbone pipeline of the application, forming the pipeline between Extracting Transforming and Loading of the scraped data.

This path includes:
- REST API Methods to intake new data from an external scraping application
- REST API to query data in the form of raw data and processed reports to pass onto a front0end
- Connection to store the processed reports externally in a database
- Data cleaning jobs that clean through the data prior to storage within the Database
- Automation scripts to arrange the jobs

Currently runs a task queue through different stages of jobs, before finally outputting over to an
SQLite database

Presentation Layer - inboundAPI and outboundAPI
Business Logic Layer - processing > intakejob and reportjob
Persistence Layer - databaseConn > DAO

-----

runjob.py should start all related servers with their ports
currently starts Flask api

`py -m celery --app celeryBroker worker --loglevel=INFO -B -s ./data/beat.schedule`

Flask 

The inboundAPI is now currently activated via runjob.py within root, which triggers api.py:

`py inboundAPI.py`

In the end we will want a full script (perhaps a shell script) that activates all servers and ports

Test API script 

`py inboundAPI/testapi.py`

Test Pipeline Task Queue

`py testscheduler.py`

TODO: Use marshmallow for json schema validation and serialisation

-----

SQL Debugging:

SQLite CLI tool

`sqlite3 <dbname>` 

sqlbrowser

`sqlitebrowser`

Technologies and Libraries:
- Python 3.10
- Flask - micro web framework for REST API
- PySpark - multithreaded data processing
- Pandas - Data manipulation
- Numpy - for graphing
- matplotlib - graphing
- RabbitMQ - message broker - requires Erlang installation
- Celery - task management framework asynchronous task queue + scheduling
- sqlite3 - for DB connectivity
- SpaCY for NLP jobs
- PyArrow for parquet support

TODO: Wrap up dependencies within Docker

------


Schema for the SQLite database table 'articles':
```
	"id"	INTEGER NOT NULL UNIQUE,
	"title"	TEXT NOT NULL,
	"author"	TEXT NOT NULL,
	"project"	TEXT NOT NULL,
	"date_published"	TEXT,
	"lead_image_url"	TEXT,
	"content"	TEXT NOT NULL,
	"next_page_url"	TEXT,
	"url"	TEXT NOT NULL,
	"domain"	TEXT,
	"excerpt"	TEXT,
	"word_count"	INTEGER,
	"direction"	TEXT,
	"total_pages"	INTEGER,
	"rendered_pages"	TEXT,
	"keywords"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
```