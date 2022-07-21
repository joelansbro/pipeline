# runs after the cleaning job, will run NLP and extract keywords to then store into the SQLite database

import os
import glob
import time
import sqlite3
from config import SQLITE_DATABASE

insert_test = """INSERT INTO "articles" 
(id, title, author, project, date_published, lead_image_url, content, next_page_url, url, domain, excerpt, word_count, direction, total_pages, rendered_pages, keywords) 
VALUES 
('{id}', '{title}', '{author}', '{project}', '{date_published}', '{lead_image_url}', '{content}', '{next_page_url}', '{url}', '{domain}', '{excerpt}', '{word_count}', '{direction}', '{total_pages}', '{rendered_pages}', '{keywords}')"""

def keywordjob():
    print("keywordjob is now running")
    
    for root, dirs, files in os.walk('./data/cleaned/'):
        files = glob.glob(os.path.join(root,'*.txt'))
        for f in files:
            print(f)
    
    time.sleep(10)

    with open('./data/keyword/keyword.txt','w') as f:
        f.write('output of keywordjob.py')

    try:
        sqliteConnection = sqlite3.connect(SQLITE_DATABASE)
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")

        count = cursor.execute(
            insert_test.format(
                id=2,
                title="article_test",
                author="Joel",
                project="dev",
                date_published="2022-05-04",
                lead_image_url="https://google.com",
                content="This is a test to ensure the SQLite connection works from the keywords jobs",
                next_page_url="na",
                url="https://joelansbro.com",
                domain="not sure if this is like category or website",
                excerpt="Test article",
                word_count=20,
                direction="right",
                total_pages=1,
                rendered_pages=1,
                keywords="Python, Jupyter, SQLite"
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