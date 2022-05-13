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



from flask import Flask, request
from sqlalchemy import null

app = Flask(__name__)

class JsonPayload():
    # object for the JSONPayload received
    def __init__(self):
        self.title = title


@app.route('/query-example', methods=['POST'])
def query_example():
    # for passing via a single POST method without JSON
    title = request.args['title']
    # etc etc

@app.route('/json-example', methods=['POST'])
def json_example():
    request_data = request.get_json()

# I've created an article object in order to pass the data round more easily, within serializer.py

    title = None
    author = None
    project = None
    date_published = None 
    lead_image_url = None
    content = None
    next_page_url = None 
    url = None
    domain = None
    excerpt = None
    word_count = None 
    direction = None
    total_pages = None 
    rendered_pages = None  

    if request_data:
        title = request_data['title']
        author = request_data['author']
        project = request_data['project']
        date_published = request_data['date_published']
        lead_image_url = request_data['lead_image_url']
        content = request_data['content']
        next_page_url = request_data['next_page_url']
        url = request_data['url']
        domain = request_data['domain']
        excerpt = request_data['excerpt']
        word_count = request_data['word_count']
        direction = request_data['direction']
        total_pages = request_data['total_pages']
        rendered_pages = request_data['rendered_pages']

    return '''
    title = {}
    author = {}
    project = {}
    date_published = {} 
    lead_image_url = {}
    content = {}
    next_page_url = {} 
    url = {}
    domain = {}
    excerpt = {}
    word_count = {} 
    direction = {}
    total_pages = {} 
    rendered_pages = {}  
    '''.format(title,author,project,date_published,lead_image_url,content,next_page_url,url,domain,excerpt,word_count,direction,total_pages,rendered_pages)

def saveJson(response):
    #save down JSON locally
    return null


def sanitisaton(response):
    #sanitise input
    return null

if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, port=5000)


# look to ticket to see further, but in a nutshell:
# need to refactor
# will need to sanitise bad input re a JSON parser
# will need to add an endpoint that checks for multiple params, an event listener that continuously looks for multiple JSON files
# will need to consider other payload methods, for instance a POST where all params are within a string
