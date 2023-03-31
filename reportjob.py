import os

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from functools import partial
import tldextract
import re

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

def reading_score(exploded_content: DataFrame):
    """This function is supposed to return a dataframe with the readability scores attached."""

    """ Double-check this code, I don't think it calculates these scores correctly."""
    readable_df = exploded_content.withColumn("flesch_reading_ease", size("words") / size("sentences"))\
        .withColumn("gunning_fog_index", 2 * size("sentences") / size("sentences") + 12)
    
    return readable_df


"""Register UDFs"""
is_reputable_udf = udf(reputable_source, IntegerType())
    
def select_report(report):
    """
    This job gets all article rows from the sqlite DB and analyses the data.

    The analysis jobs for the time being can append new columns onto the data and then output to csv format.
    """

    # I've been reading that I shouldnt be committing jars to the repo but that's okay for now
    spark = SparkSession.Builder().master('local[*]')\
        .appName('keywordjob')\
        .config(
        'spark.jars', 
        '{}/sqlite-jdbc-3.34.0.jar'.format(os.getcwd())
        )\
        .config(
        'spark.driver.extraClassPath',
        '{}/sqlite-jdbc-3.34.0.jar'.format(os.getcwd())
        )\
        .getOrCreate()

    """Load in the dataframe and split the content for analysis"""
    articles = spark.read.format("jdbc")\
        .options(url ="jdbc:sqlite:./data/maindb.sqlite", dbtable="articles")\
        .load()\
        .withColumn("sentences", sentences("content"))\
        .withColumn("words", flatten("sentences"))
    

    """Create statistics for the credibility score"""
    reputable_df = articles.withColumn('reputable_source', is_reputable_udf('url'))\

    readability_df = reading_score(reputable_df)

    """Output the dataframe"""
    output_df = readability_df.select('title','reputable_source','flesch_reading_ease','gunning_fog_index')
    output_df.write.option("header",True).mode('overwrite').csv('./data/output/report')

if __name__=='__main__':
    select_report('None')