import requests
from pymongo import MongoClient
from config import Config

def get_profile():
    client = MongoClient(Config.MONGO_URL)
    db = client[Config.DB_NAME]
    collection = db[Config.COLLECTION_NAME]

    token_doc = collection.find_one({"dhanClientId": Config.DHAN_CLIENT_ID})

    if not token_doc:
        print("❌ No token found. Please login first.")
        return

    headers = {
        "access-token": token_doc["accessToken"]
    }

    response = requests.get(Config.PROFILE_URL, headers=headers)
    print(response.json())