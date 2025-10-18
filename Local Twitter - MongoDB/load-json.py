"""
Project Name : Project 2
File Purpose : Loading data from JSON files to MongoDB using Python
CCID & Name  : yaathesh & Yaatheshini Ashok Kumar
CCID & Name  : vsivakum & Vishal Sivakumar
"""

import sys
import json
from pymongo import MongoClient

n = len(sys.argv)
# Checking if correct number of command line arguements are provided
if n != 3:
    print("- Error: Incorrect Number of Arguments -")
    sys.exit(0)

client = MongoClient('localhost', int(sys.argv[1]))
db = client['291db']        # Accessing or creating a database
collist = db.list_collection_names()        # Accessing or creating a collection

# Checking if the tweets collection already exists
if "tweets" in collist:
    print("- Tweets exists. -")

# Accessing a 'tweets' collection in the '291db' database
tweets = db["tweets"]

# Deleting all data from the 'tweets' collection
tweets.delete_many({})

# Opening the file for reading
f = open(sys.argv[2],'r')
data = []
for line in f:
    data.append(json.loads(line))

f.close()       # Closing the file

# Inserting data into the 'tweets' collection in batches
batch = []
batch_size = 10000

for i in range(0, len(data), batch_size):
    batch = data[i:i+batch_size]
    if batch:
        tweets.insert_many(batch)
