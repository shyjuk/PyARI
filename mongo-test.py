
import pymongo

from pymongo import MongoClient
client = MongoClient()

db = client.voiceinn_prot
print db

collection = db.organization
print collection.find_one()
