# runs after the intake job, goes through the batched data and cleans it all
from distutils.log import error
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime
import random
import os
import glob
import time

def cleanjob():

    spark = SparkSession.Builder().master('local[*]')\
        .appName('cleanjob')\
        .getOrCreate()

    spark.conf.set("mapreduce.fileoutputcommitter.marksuccessfuljobs", "false")

    print("cleanjob is now running")
    # for root, dirs, files in os.walk('./data/collated/'):
    #     file = glob.glob(os.path.join(root,'*.parquet'))
    file = './data/collated'
    try:
            current_data = spark.read.parquet(file)
            current_data.printSchema()
            print("Parquet data is valid")

                # To insert into DB successfully
            
            comma_data = current_data\
                .withColumn('content', regexp_replace("content","'","`"))\
                .withColumn('excerpt', regexp_replace("excerpt","'","`"))\
                .withColumn('content', regexp_replace("content","quot;&quot;&quot"," "))\
                .withColumn('title', regexp_replace("title","'","`"))\
                .withColumn('content', regexp_replace("content", "\n",""))\
                .withColumn('content', regexp_replace("content", "<.+?>",""))\
                #.withColumn('content', regexp_replace("content","""<(?!\/?a(?=>|\s.*>))\/?.*?>""",""))\ # this takes all html but leaves the <a> refs
            
            # the word count was wrong from the json, so I recounted them
            word_counted = comma_data.withColumn("word_count", size(split(col("content"), " ")))

            # To fix this - untested
            # if the end url route is longer than the title of the article, replace with the end route
            # replaced_title = word_counted\
            #     .withColumn("title", 
            #         when((length("title") > length(split("url","/")[-1])), "route").otherwise(col("title")))

            word_counted.show(n=100,truncate=True)
            print(word_counted.count())
            print("Closing this Parquet")
                
            parquet_name = "{:%Y%m%d%H%M}00".format(datetime.now()) + str(random.randint(1,10000))
            save_loc = 'data/cleaned/{}.parquet'.format(parquet_name)
                
            word_counted.coalesce(1).write.parquet(save_loc)
            time.sleep(2)
                
    except error:
            print("Error occurred ", error)
    
    print("clean job completed")
    
    spark.stop()
    time.sleep(5)

if __name__ == '__main__':
    cleanjob()