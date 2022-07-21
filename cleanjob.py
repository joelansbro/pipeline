# runs after the intake job, goes through the batched data and cleans it all
import os
import glob
import time

def cleanjob():
    print("cleanjob is now running")
    
    for root, dirs, files in os.walk('./data/collated/'):
        files = glob.glob(os.path.join(root,'*.csv'))
        for f in files:
            print(f)
    
    time.sleep(10)
    print("clean job completed")

    with open('./data/cleaned/cleaned.txt','w') as f:
        f.write('output of cleanjob.py')