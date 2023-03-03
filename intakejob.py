# this module will intake raw data from the raw storage location and process to put into reports
# raw data should be appended with an identifier to signify  what project it is a part of 
# data is cleansed and stored in the database in a combined storage file / table
# files / tables are divided by their identifier connected to the scrape job "project" performed

# business logic layer

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

    df = spark.read.json("./data/stash/*json")

    df.collect()
    save_loc = 'data/collated/{}.parquet'.format(parquet_name())
    df.write.parquet(save_loc)

    print("Exiting process now")
    spark.stop()
    time.sleep(5)


if __name__ == '__main__':
    intakejob()
