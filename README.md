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
