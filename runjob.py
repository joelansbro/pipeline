# this starting script designates the start of other processes.
# processes that need to be ran: database connection, inboundAPI, outboundAPI, 
# if this runjob is active, maintain a server connection for the inboundAPI
# automate processing job to take affect every thirty minutes or so (define specifically)


"""
This is a test

"""
# This module will define the API endpoints to listen in to the scraped data
# acts as a receiver to pass along the data to a raw storage location
# inbound data from this api needs to be appended with an identifier to point out what scraping job it belongs to

# contains code that implements the external APIs

# we dont at this stage have to worry about assigning a unique identifier here, 
# as The ObjectID is the primary key for the stored document and is automatically generated when creating a new document in a collection
# https://www.mongodb.com/docs/manual/reference/method/ObjectId/
# this project must create the JSON in the following schema:

# title string
# author string
# project - individual project assignment for report tracking string
# date_published int
# lead_image_url string
# content string
# next_page_url string
# url string
# domain string
# excerpt string
# word_count int
# direction string
# total_pages int
# rendered_pages int
# keywords array[string]

# unsure at this stage what particular values to enforce, and which could be null (ie: keywords likely null and created later)

# good guide - https://www.digitalocean.com/community/tutorials/processing-incoming-request-data-in-flask
# also, two cool tools to use - fuzzer testing - github.com/Endava/cats
# Mitmproxy2swagger - reverse engineer REST APIs to see what others are doing - github.com/alufers/mitmproxy2swagger


"""
This below is currently a test to ensure that I can get a Docker file up and running, this should expose a port for API use
"""


from celery import Celery

app = Celery('tasks', broker='pyamqp://guest@localhost//')

@app.task
def add(x, y):
    return x + y