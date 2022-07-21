# runs after the cleaning job, will run NLP and extract keywords to then store into the SQLite database

import os
import glob
import time

def keywordjob():
    print("keywordjob is now running")
    
    for root, dirs, files in os.walk('./data/cleaned/'):
        files = glob.glob(os.path.join(root,'*.txt'))
        for f in files:
            print(f)
    
    time.sleep(10)
    print("keyword job completed")

    with open('./data/keyword/keyword.txt','w') as f:
        f.write('output of keywordjob.py')