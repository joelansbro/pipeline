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

    print("cleanjob is now running")
    for root, dirs, files in os.walk('./data/collated/'):
        files = glob.glob(os.path.join(root,'*.parquet'))
        try:
            for f in files:
                current_data = spark.read.parquet(f)
                current_data.printSchema()
                print("Parquet data is valid")
                current_data.show(n=100,truncate=True)
                # To insert into DB successfully
                comma_data = current_data.withColumn('content', regexp_replace("content","'","`"))
                comma_data = current_data.withColumn('excerpt', regexp_replace("excerpt","'","`"))
                comma_data = current_data.withColumn('title', regexp_replace("title","'","`"))
                print(comma_data.count())
                print("Closing this Parquet")
                
                parquet_name = "{:%Y%m%d%H%M}00".format(datetime.now()) + str(random.randint(1,10000))
                save_loc = 'data/cleaned/{}.parquet'.format(parquet_name)
                
                comma_data.write.parquet(save_loc)
                time.sleep(2)
                
        except error:
            print("Error occured ", error)
    
    print("clean job completed")
    spark.stop()
    time.sleep(5)

    # with open('./data/cleaned/cleaned.txt','w') as f:
    #     f.write('output of cleanjob.py')