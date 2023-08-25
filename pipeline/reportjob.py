import re
import statistics
import string
import json
import multiprocessing

import sqlite3
import pandas as pd
import nltk
import itertools

# NLP modules
import enchant
import tldextract

import spacy
from spacy_arguing_lexicon import ArguingLexiconParser
from spacy.language import Language
from spacytextblob.spacytextblob import SpacyTextBlob
import textdescriptives as td


"""Set Up NLP Models"""
# create a dictionary object for the English language
english_dict = enchant.DictWithPWL("en_US", "my_pwl.txt")

# Create the spacy nlp pipeline
# will load a separate model for the topic classifier
nlp = spacy.load("en_core_web_sm")
nlpmd = spacy.load("en_core_web_md")


@Language.factory("ArguingLexiconParser", default_config={"lang":nlp.lang})
def CreateArguingLexiconParser(nlp, name, lang):
    return ArguingLexiconParser()

# load in the topic modellers for the classifier
try:
    with open('topic_oneshot.json', 'r') as json_file:
        # Load the JSON data from the file
        topic_data = json.load(json_file)
except FileNotFoundError:
    print(f"The file was not found.")
except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")


"""NLP Functions"""

def spelling_mistakes_udf(nlp, content):
    """Function to count the number of spelling mistakes in a string"""
    doc = nlp(content)
    mistake_count = 0
    for token in doc:
        try:
            if not english_dict.check(token.text.strip(string.punctuation)):
                mistake_count += 1
        except ValueError as e:
            continue
    return mistake_count

def spelling_mistakes(df):
    df['num_spelling_mistakes'] = df.apply(lambda row: spelling_mistakes_udf(nlp, row['content']), axis=1)
    return df

def reputable_source(url: str):
    """Checks if the blog article is from a reputable source.
    
    In future could load in a separate CSV of locations for this task, 
    but this will be fine as a proof of concept.
    """

    with open('rep_websites.txt') as file:
        contents = file.read()
        lines = contents.split('\n')
        reputable_websites = [line for line in lines if line.strip()]

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

def text_descriptives_udf(content):
    doc = nlp(content)
    
    return pd.Series(
        [
            doc._.readability['flesch_reading_ease'],
            doc._.readability['gunning_fog'],
            doc._.token_length['token_length_mean'],
            doc._.syllables['syllables_per_token_mean'],
            doc._.coherence['first_order_coherence'],
            doc._.coherence['second_order_coherence'],
            doc._.information_theory['entropy'],
            doc._.information_theory['perplexity']
        ]
    )    

def text_descriptives(df):
    df[[
        'flesch_reading_ease',
        'gunning_fog',
        'mean_token_length',
        'syllables_per_token',
        'first_order_coherence',
        'second_order_coherence',
        'entropy', 
        'perplexity'
    ]] = df.apply(
            lambda row: text_descriptives_udf(row['content']), axis = 1)
    return df

def parse_specifics_udf(words):
    """Counting up specific markers within the word lists of the text."""
    experience_markers = ["i", "me", "we", "my", "experience"]
    experience_count = sum(1 for word in words if word.lower() in experience_markers)

    temporal_markers = ["yesterday", "today", "tomorrow", "last", "this", "next"]
    temporal_count = sum(1 for word in words if word.lower() in temporal_markers)

    past_tense_count = sum(1 for word in words if word.lower().endswith("ed"))
    gerund_count = sum(1 for word in words if word.lower().endswith("ing"))

    return pd.Series([
        experience_count,
        temporal_count,
        past_tense_count,
        gerund_count,
    ])

def parse_specifics(df):
    df[[
        'experience_count',
        'temporal_count',
        'past_tense_count',
        'gerund_count',
    ]] = df.apply(
        lambda row: parse_specifics_udf(row['words']), axis = 1)
    return df

def get_meta_links_udf(content):
    """Simpler finds that rely upon entire content chunks"""
    # this one gets the marks of whether a blog articles mentions that it is sponsored
    sponsored_markers = ["our sponsor", "sponsored by", "funded by", "our funder", "brought to you by", "presented by",
                         "supported by", "our supporter", "paid for by", "this article is brought", "this content is brought",
                         "sponsored content"]
    sponsored_count = sum(1 for word in content if word.lower() in sponsored_markers)

    # count up the number of urls that are not local hosts to try to find sources of linked content
    url_pattern = r'https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    matches = re.findall(url_pattern, content)
    filtered_matches = [url for url in matches if not re.match(r'https?://(localhost|\d+\.\d+\.\d+\.\d+)', url)]
    reference_count = len(filtered_matches)

    return pd.Series([
        sponsored_count,
        reference_count
    ])

def get_meta_links(df):
    df[[
        'sponsor_count',
        'reference_count'
    ]] = df.apply(
        lambda row: get_meta_links_udf(row['content']), axis = 1)
    return df


def get_topic_score_udf(row):
    """Set to return the entry in the dict that corresponds to the json file passed in. 
    
    Get the aggregated score of both the title and excerpt, the content score is 
    prohibitively expensive for my CPU.
    Uses typeform/distilbert-base-uncased-mnli to be found here:
    https://huggingface.co/typeform/distilbert-base-uncased-mnli
    """
    title_score = nlpmd(row['title'])._.cats['high-performance-teams']
    excerpt_score = nlpmd(row['excerpt'])._.cats['high-performance-teams']
    mean = statistics.mean([title_score, excerpt_score, excerpt_score])
    print(mean)
    return mean

# def text_categorizer(df):
#     """For getting the topic score related to the topic at hand"""
#     df['topic_score'] = df.apply(lambda row: get_topic_score_udf(row['title'], row['content']),  axis = 1)
#     return df

def text_categorizer_parallel(df):
    num_cores = 4  # max cores 8, want to conserve some cpu
    pool = multiprocessing.Pool(processes=num_cores)  # Create a pool of worker processes

    # Use the map function to apply get_topic_score_udf to each row in parallel
    df['topic_score'] = pool.map(get_topic_score_udf, df.itertuples(index=False))

    pool.close()
    pool.join()
    
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
            """            
                SELECT *
                FROM articles
                WHERE project = '{}'
            """.format(report),
            conn
            )
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
    conn.close()

    # pandas preprocessing
    df = df.drop(columns=['id'])
    df = df.drop_duplicates()
    df['sentences'] = df['content'].apply(nltk.sent_tokenize)
    df['words'] = df['sentences'].apply(lambda s: list(itertools.chain.from_iterable([nltk.word_tokenize(sentence) for sentence in s])))

    # NLP operations
    print("Counting spelling mistakes")    
    df = spelling_mistakes(df)

    print("Checking source of articles")
    df['source_reputation'] = df['url'].apply(reputable_source)

    nlp.add_pipe("ArguingLexiconParser")
    print("Parsing arguments")
    df = arg_mining(df)
    nlp.remove_pipe("ArguingLexiconParser")

    nlp.add_pipe("spacytextblob")
    print("Getting Sentiment")
    df = sentiment_analysis(df)
    nlp.remove_pipe("spacytextblob")

    nlp.add_pipe("textdescriptives/all")
    print("Getting Text Descriptives")
    df = text_descriptives(df)
    nlp.remove_pipe("textdescriptives/all")

    print("parsing specifics")
    df = parse_specifics(df)
    print("getting metalinks")
    df = get_meta_links(df)

    print("getting title categories")
    nlpmd.add_pipe("text_categorizer",
             config={
                 "data": topic_data,
                 "model": "typeform/distilbert-base-uncased-mnli",
                 "cat_type": "zero",
                 "device":"cpu"
             })
    df = text_categorizer_parallel(df)
    nlpmd.remove_pipe("text_categorizer")

    print("All done! Saving...")
    # outputs a dataframe
    df_selected = df[[
        'id',
        'title',
        'keywords',
        'author',
        'project',
        'url',
        'domain',
        'word_count',
        'excerpt',
        'content',
        'date_published',
        'num_spelling_mistakes',
        'source_reputation',
        'num_of_arg_phrases',
        'polarity',
        'subjectivity',
        'sentiment',
        'flesch_reading_ease',
        'gunning_fog',
        'mean_token_length',
        'syllables_per_token',
        'first_order_coherence',
        'second_order_coherence',
        'entropy', 
        'perplexity',
        'experience_count',
        'temporal_count',
        'past_tense_count',
        'gerund_count',
        'sponsor_count',
        'reference_count',
        'topic_score'
        ]]
    df_selected.to_csv('../data/output/report/output.csv')

if __name__=='__main__':
    select_report('highperformanceteams')