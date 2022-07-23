# runs after the cleaning job, will run NLP and extract keywords to then store into the SQLite database
from ast import keyword
from distutils.log import error
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import os
import glob
import time
import sqlite3
from config import SQLITE_DATABASE


"""
Currently this job outputs the same parquet information twice, the parquet input holds it twice.
This is likely because of the way we are saving down the parquet in the previous step is via pysparks method
however if we did it via pyarrow this may work better

alternative would be to check the DB for duplicate rows given the project and title, before inserting the data


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

def check_db_for_dupe(input):
    """
    input article.title, article.project
    select statement to db:
        where title = article.title and project = article.project
        if so, pass
        else, send article to pass_to_sql()

    """
    return True

def keywordjob():
    print("keywordjob is now running")
    
    spark = SparkSession.Builder().master('local[*]')\
        .appName('keywordjob')\
        .getOrCreate()

    for root, dirs, files in os.walk('./data/cleaned/'):
        files = glob.glob(os.path.join(root,'*.parquet'))
        try:
            for f in files: # this has saved the single article down double, you need to iterate only once at a certain part
                print(f)
                current_data = spark.read.parquet(f)
                # this may work for the time being but will 100% not work on larger datasets
                row_list = current_data.collect()
                for row in row_list:
                    article = parquet_to_object(row)
                    print(article.title)
                    print(article.author)
                    pass_to_sql(article)

        except error:
            print("Error occured ", error)

def parquet_to_object(row):
    
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
        keywords = "test_keywords"
    )
    print(par_article.title)
    print(par_article.author)
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
                print("End connection to database")


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


# if __name__ == '__main__':
#     keywordjob()