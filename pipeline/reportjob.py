import sqlite3
import pandas as pd
import enchant
import tldextract
import numpy as np
import nltk # uses punkt
import itertools
from textstat import flesch_reading_ease, gunning_fog
import re

"""I may have to use pandas instead to construct this nlp job."""

"""[
    id: int, 
    title: string, 
    author: string, 
    project: string, 
    date_published: string, 
    lead_image_url: string, 
    content: string, 
    next_page_url: string, 
    url: string, 
    domain: string, 
    excerpt: string, 
    word_count: int, 
    direction: string, 
    total_pages: int, 
    rendered_pages: string, 
    keywords: string
    ]

    We have a lot of things we could take from textstat as well:
    textstat.flesch_reading_ease(test_data)
    textstat.flesch_kincaid_grade(test_data)
    textstat.smog_index(test_data)
    textstat.coleman_liau_index(test_data)
    textstat.automated_readability_index(test_data)
    textstat.dale_chall_readability_score(test_data)
    textstat.difficult_words(test_data)
    textstat.linsear_write_formula(test_data)
    textstat.gunning_fog(test_data)
    textstat.text_standard(test_data)
    textstat.fernandez_huerta(test_data)
    textstat.szigriszt_pazos(test_data)
    textstat.gutierrez_polini(test_data)
    textstat.crawford(test_data)
    textstat.gulpease_index(test_data)
    textstat.osman(test_data)
"""
# create a dictionary object for the English language
english_dict = enchant.DictWithPWL("en_US", "my_pwl.txt")


"""NLP Functions"""

def count_spelling_mistakes(sentence):
    """Function to count the number of spelling mistakes in a string"""
    num_misspelled = sum([not english_dict.check(word.lower()) for word in sentence])
    return num_misspelled

def add_reading_scores(df):
    df['flesch_reading_ease'] = df.apply(lambda row: flesch_reading_ease(row['content']), axis=1)
    df['gunning_fog'] = df.apply(lambda row: gunning_fog(row['content']), axis=1)    
    return df

def reputable_source(url: str):
    """Checks if the blog article is from a reputable source.
    
    In future could load in a separate CSV of locations for this task, 
    but this will be fine as a proof of concept.
    """
    reputable_websites = {'apple.com', 'shopify.com', 'science.org', 'ieee.org', 'news.ycombinator.com'}
    reputable_suffixes = {'org', 'edu', 'ac', 'gov'}

    points = 0

    extracted = tldextract.extract(url)
    if extracted.registered_domain in reputable_websites:
        points += 1
    
    for suffix in reputable_suffixes:
        if re.search(r"\." + suffix + r"(?:\.[a-z]+)?$", url):
            points += 1
    
    return points



def select_report(report: str):
    """
    This job gets all article rows from the sqlite DB and analyses the data.

    The analysis jobs for the time being can append new columns onto the data and then output to csv format.
    """
    
    try:
        # connect to the SQLite database
        conn = sqlite3.connect('./data/maindb.sqlite')
        df = pd.read_sql_query(
            "SELECT * FROM articles WHERE project = '{}'".format(report),
            conn
            )
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
    conn.close()

    df['sentences'] = df['content'].apply(nltk.sent_tokenize)
    df['words'] = df['sentences'].apply(lambda s: list(itertools.chain.from_iterable([nltk.word_tokenize(sentence) for sentence in s])))
    

    # NLP operations
    df['num_spelling_mistakes'] = df['words'].apply(
        lambda sentence_list: sum([
            count_spelling_mistakes(sentence) for sentence in sentence_list]))

    df['source_reputation'] = df['url'].apply(reputable_source)

    df = add_reading_scores(df)


    # outputs a dataframe
    df_selected = df[['title','num_spelling_mistakes','source_reputation','flesch_reading_ease', 'gunning_fog']]
    df_selected.to_csv('./data/output/report/output.csv')


if __name__=='__main__':
    select_report('None')