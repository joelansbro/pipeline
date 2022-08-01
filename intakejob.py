# this module will intake raw data from the raw storage location and process to put into reports
# raw data should be appended with an identifier to signify  what project it is a part of 
# data is cleansed and stored in the database in a combined storage file / table
# files / tables are divided by their identifier connected to the scrape job "project" performed

# business logic layer

import jsonschema
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import pyarrow as pa
import pyarrow.parquet as pq
import glob
import os
import pandas as pd
import time
from pipe_utils import parquet_name

def intakejob():

    spark = SparkSession.Builder().master('local[*]')\
        .appName('inboundcollation')\
        .getOrCreate()


    jsonSchema = StructType([
    StructField("title", StringType(), False),
    StructField("author", StringType(), True),
    StructField("project", StringType(), False),
    StructField("date_published", StringType(), True),
    StructField("lead_image_url", StringType(), True),
    StructField("content", StringType(), False),
    StructField("next_page_url", StringType(), True),
    StructField("url", StringType(), False),
    StructField("domain", StringType(), True),
    StructField("excerpt", StringType(), True),
    StructField("word_count", IntegerType(), False),
    StructField("direction", StringType(), True),
    StructField("total_pages", IntegerType(), True),
    StructField("rendered_pages", IntegerType(), True),
    ])

    all_files = []

    for root, dirs, files in os.walk('./data/stash/'):
        files = glob.glob(os.path.join(root,'*.json'))
        for f in files:
            all_files.append(os.path.abspath(f))

    def create_empty_dataframe():
        index = pd.Index([], name="id", dtype=int)
        # specify column name and data type 
        columns = [ # need to add in here a unique identifier (optional, if none, SQLite will create one afterwards)
               ('title', str),
               ('author', str),
               ('project', str),
               ('date_published', str),
               ('lead_image_url', str),
               ('content', str),
               ('next_page_url', str),
               ('url', str),
               ('domain', str),
               ('excerpt', str),
               ('word_count', int),
               ('direction', str),
               ('total_pages', int),
               ('rendered_pages', int)]
        # create the dataframe from a dict
        return pd.DataFrame({k: pd.Series(dtype=t) for k, t in columns})



    #  I may need to create a default schema file if I go with this method
    df_app = spark.read.schema(jsonSchema).json("./data/stash/1234.json", multiLine=True)
    pandas = df_app.toPandas()
    print(pandas)


    emptyDF = create_empty_dataframe()

    for file in all_files:
        df_app = spark.read.schema(jsonSchema).json(file, multiLine=True)
        print(df_app)
        pandas = df_app.toPandas()
        emptyDF = pd.concat([emptyDF, pandas])
        time.sleep(1)
        print("Added a new article to batch")

    save_loc = 'data/collated/{}.parquet'.format(parquet_name())

    save_down = pa.Table.from_pandas(emptyDF, preserve_index=False)
    pq.write_table(table=save_down, where=save_loc)

    print("Exiting process now")
    spark.stop()
    time.sleep(5)