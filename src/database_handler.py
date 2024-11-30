from pymongo import MongoClient

def connect_to_db(uri, db_name):
    client = MongoClient(uri)
    db = client[db_name]
    return db

def save_to_db(data, db, collection_name):
    collection = db[collection_name]
    collection.insert_many(data.to_dict('records'))