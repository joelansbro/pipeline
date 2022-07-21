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
                # current_data.show(True)
                # this show is currently broken, see stack trace below
                print("Closing this Parquet")
                 
                parquet_name = "{:%Y%m%d%H%M}00".format(datetime.now()) + str(random.randint(1,10000))
                save_loc = 'data/cleaned/{}.parquet'.format(parquet_name)
                
                current_data.write.parquet(save_loc)
                
        except error:
            print("Error occured ", error)
    
    time.sleep(10)
    print("clean job completed")

    # with open('./data/cleaned/cleaned.txt','w') as f:
    #     f.write('output of cleanjob.py')


"""
                ERROR/ForkPoolWorker-9] Task celeryBroker._chainfileprocessing[a37353a4-5b0e-4b38-87d6-6b43cb4785c9] raised unexpected: TypeError('catching classes that do not inherit from BaseException is not allowed')
                Traceback (most recent call last):
                File "/home/joel/Documents/pipeline/cleanjob.py", line 29, in cleanjob
                current_data.show(True)
                File "/home/joel/.local/lib/python3.8/site-packages/pyspark/sql/dataframe.py", line 488, in show
                raise TypeError("Parameter 'n' (number of rows) must be an int")
                TypeError: Parameter 'n' (number of rows) must be an int

                """