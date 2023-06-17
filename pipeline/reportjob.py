import sqlite3
import pandas as pd
import enchant
import tldextract
import numpy as np
import nltk # uses punkt
import itertools
from textstat import flesch_reading_ease, gunning_fog
import re

import statistics

import spacy
from spacy_arguing_lexicon import ArguingLexiconParser
from spacy.language import Language
from spacytextblob.spacytextblob import SpacyTextBlob


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

"""

"""Set Up NLP Models"""
# create a dictionary object for the English language
english_dict = enchant.DictWithPWL("en_US", "my_pwl.txt")

# Create the spacy nlp pipeline
nlp = spacy.load("en_core_web_sm")

@Language.factory("ArguingLexiconParser", default_config={"lang":nlp.lang})
def CreateArguingLexiconParser(nlp, name, lang):
    return ArguingLexiconParser()

nlp.add_pipe("ArguingLexiconParser")
nlp.add_pipe("spacytextblob")

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

def arg_mining_udf(nlp, sentences):
    """UDF for arg_mining column"""
    total_count = 0

    for sentence in sentences:
        try:
            doc = nlp(sentence)
            argument_span = next(doc._.arguments.get_argument_spans())
            total_count += len(argument_span)
        except StopIteration:
            continue
    print(total_count)
    return total_count

def arg_mining(df):
    df['num_of_arg_phrases'] = df.apply(lambda row: arg_mining_udf(nlp, row['sentences']), axis=1)
    return df


def sentiment_analysis_udf(nlp, content, keywords):
    doc = nlp(content)

    content_polarity = doc._.blob.polarity
    content_subjectivity = doc._.blob.subjectivity

    # now get keyword sentiment

    key_sentiments_list = []
    # split each keyword into a separate sentence to analyse
    # rounding keywords due to their importance to the text
    keyword_list = keywords.split(',')
    for keyword in keyword_list:
        doc = nlp(keyword)
        if doc._.blob.polarity > 0:
            key_polarity = -1
        elif doc._.blob.polarity == 0:
            key_polarity = doc._.blob.polarity
        else:
            key_polarity = 1
        key_sentiments_list.append(key_polarity)

    # bias keywords in sentiment analysis
    keyword_total_score = statistics.mean(key_sentiments_list)

    ensemble_sentiment_score = statistics.mean([
        content_polarity, keyword_total_score, keyword_total_score
        ])
    
    if ensemble_sentiment_score >= 0.0:
        sentiment = 'POSITIVE'
    else:
        sentiment = 'NEGATIVE'

    return pd.Series(
        [
            ensemble_sentiment_score,
            content_subjectivity,
            sentiment
        ]
    )

def sentiment_analysis(df):
    df[['polarity','subjectivity','sentiment']] = df.apply(
        lambda row: sentiment_analysis_udf(nlp, row['content'], row['keywords']), axis=1)
    return df


def select_report(report: str):
    """
    This job gets all article rows from the sqlite DB and analyses the data.

    The analysis jobs for the time being can append new columns onto the data and then output to csv format.
    """
    
    try:
        # connect to the SQLite database
        conn = sqlite3.connect('../data/maindb.sqlite')
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
    print("Counting spelling mistakes")
    df['num_spelling_mistakes'] = df['words'].apply(
        lambda sentence_list: sum([
            count_spelling_mistakes(sentence) for sentence in sentence_list]))
    print("Checking source of articles")
    df['source_reputation'] = df['url'].apply(reputable_source)

    print("Parsing readability scores")
    df = add_reading_scores(df)

    print("Parsing arguments")
    df = arg_mining(df)

    print("Getting Sentiment")
    df = sentiment_analysis(df)

    print("All done! Saving...")
    # outputs a dataframe
    df_selected = df[[
        'title',
        'keywords',
        'author',
        'project',
        'url',
        'num_spelling_mistakes',
        'source_reputation',
        'flesch_reading_ease',
        'gunning_fog',
        'num_of_arg_phrases',
        'polarity',
        'subjectivity',
        'sentiment'
        ]]
    df_selected.to_csv('../data/output/report/output.csv')


if __name__=='__main__':
    select_report('None')