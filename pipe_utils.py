import random
from w3lib.html import replace_entities
from pyspark.sql.functions import udf
from datetime import datetime

# This module contains any kind of script or object that is used in different scripts



# Save down the file with a unique identifier
def parquet_name():
    return "{:%Y%m%d%H%M}00".format(datetime.now()) + str(random.randint(1,10000))


""" Converting function to UDF """
entity_UDF = udf(lambda content: replace_entities(content))