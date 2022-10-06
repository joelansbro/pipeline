from ast import keyword
from distutils.log import error
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import os
import glob
import time
import sqlite3
import spacy
from collections import Counter
from string import punctuation
from config import SQLITE_DATABASE

"""
The keyword job takes in the content column for each article and surmises what the unique keywords are for each.
It then saves this down as another column, keywords.

Then finally, it will open a database connection an insert the article into a new row. (TODO: Add this into a separate folder within the pipeline?)


Here is 'articles' schema:
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
"""

def keywordjob():

    spark = SparkSession.Builder().master('local[*]')\
        .appName('keywordjob')\
        .getOrCreate()

    nlp = spacy.load("en_core_web_sm")
    try:

        current_data = spark.read.option("header","true").option("recursiveFileLookup","true").parquet("./data/cleaned")

        current_data.show()
        row_list = current_data.collect()

        for row in row_list:
            keyword_list = generate_keywords(row, nlp)
            article = parquet_to_object(row, keyword_list)
            print(article.title)
            print(article.author)
            print(article.keywords)
            pass_to_sql(article)

    except error:
        print("Error occured", error)

def generate_keywords(row, nlp):
    """Function gets the common words from the article content
    
    Manages to do this by storing them in a list, and converting it
    into a string for storage
    """
    keywords_output = set(get_hotwords(row['content'], nlp))
    most_common_list = Counter(keywords_output).most_common(20)
    # the most_common_list is a tuple, so I am harvesting the first element of the tuple
    ready = []
    for item in most_common_list:
        ready.append(item[0])
    keyword_list = ','.join(ready)
    
    return keyword_list

def get_hotwords(text, nlp):
    """NLP magic to gather keywords. """
    result = []
    pos_tag = ['PROPN', 'ADJ', 'NOUN', 'VERB'] 
    doc = nlp(text.lower()) 
    for token in doc:
        if(token.text in nlp.Defaults.stop_words or token.text in punctuation):
            continue
        if(token.pos_ in pos_tag):
            result.append(token.text)
    return result

def parquet_to_object(row, keyword_list):
    """Takes parquet rows and creates objects to put into database"""
    par_article = Article(
        title=row['title'],
        author=row['author'],
        project=row['project'],
        date_published=row['date_published'],
        lead_image_url=row['lead_image_url'],
        content=row['content'],
        next_page_url=row['next_page_url'],
        url=row['url'],
        domain=row['domain'],
        excerpt=row['excerpt'],
        word_count=row['word_count'],
        direction=row['direction'],
        total_pages=row['total_pages'],
        rendered_pages=row['rendered_pages'],
    # last line here errors out of course because it doesnt exist
    # keywords=row.__getitem__('keywords')
    # so for the time being:
        keywords = keyword_list
    )
    return par_article


def pass_to_sql(article):
    try:
        sqliteConnection = sqlite3.connect(SQLITE_DATABASE)
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")
        # rowid will autogenerate an id for the given table, so we do not have to concern ourselves with creating one
        count = cursor.execute(
            insert_test.format(
                title=article.title,
                author=article.author,
                project=article.project,
                date_published=article.date_published,
                lead_image_url=article.lead_image_url,
                content=article.content,
                next_page_url=article.next_page_url,
                url=article.url,
                domain=article.domain,
                excerpt=article.excerpt,
                word_count=article.word_count,
                direction=article.direction,
                total_pages=article.total_pages,
                rendered_pages=article.rendered_pages,
                keywords=article.keywords
                ))
                
        sqliteConnection.commit()
        print("Record inserted successfully into the SQLite Main Test Database for project", cursor.rowcount)
        cursor.close()

    except sqlite3.Error as error:
            print("didn't work", error)
    finally:
            if sqliteConnection:
                sqliteConnection.close()
                print("End connection to database") # this is ending the connection after each write, with so many rows being written, should we be keeping this open?


insert_test = """INSERT INTO "articles" 
(rowid, title, author, project, date_published, lead_image_url, content, next_page_url, url, domain, excerpt, word_count, direction, total_pages, rendered_pages, keywords) 
VALUES 
(NULL, '{title}', '{author}', '{project}', '{date_published}', '{lead_image_url}', '{content}', '{next_page_url}', '{url}', '{domain}', '{excerpt}', '{word_count}', '{direction}', '{total_pages}', '{rendered_pages}', '{keywords}')"""




class Article():
    def __init__(
        self,
        title,
        author,
        project,
        date_published,
        lead_image_url,
        content,
        next_page_url,
        url,
        domain,
        excerpt,
        word_count,
        direction, 
        total_pages,
        rendered_pages,
        keywords=None):
        self.title = title
        self.author = author
        self.project = project
        self.date_published = date_published
        self.lead_image_url = lead_image_url
        self.content = content
        self.next_page_url = next_page_url
        self.url = url
        self.domain = domain
        self.excerpt = excerpt
        self.word_count = word_count
        self.direction = direction
        self.total_pages = total_pages
        self.rendered_pages = rendered_pages
        self.keywords = keywords



if __name__ == '__main__':
    keywordjob()