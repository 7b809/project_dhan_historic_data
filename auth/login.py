import requests
from pymongo import MongoClient
from datetime import datetime
from config import Config


def generate_and_store_token(totp: str) -> dict:
    """
    Generate Dhan access token using TOTP,
    store it in MongoDB,
    and return status response.
    """

    try:
        # ==========================================
        # GENERATE ACCESS TOKEN
        # ==========================================
        params = {
            "dhanClientId": Config.DHAN_CLIENT_ID,
            "pin": Config.DHAN_PIN,
            "totp": totp
        }

        response = requests.post(
            Config.GENERATE_TOKEN_URL,
            params=params,
            timeout=15
        )

        if response.status_code != 200:
            return {
                "status": False,
                "message": "Token generation failed",
                "error": response.text
            }

        data = response.json()

        access_token = data.get("accessToken")
        expiry_time = data.get("expiryTime")

        if not access_token:
            return {
                "status": False,
                "message": "Access token not received",
                "error": data
            }

        # ==========================================
        # SAVE TO MONGODB
        # ==========================================
        client = MongoClient(Config.MONGO_URL)
        db = client[Config.DB_NAME]
        collection = db[Config.COLLECTION_NAME]

        token_document = {
            "dhanClientId": data.get("dhanClientId"),
            "accessToken": access_token,
            "expiryTime": expiry_time,
            "createdAt": datetime.utcnow()
        }

        # Remove old token
        collection.delete_many({
            "dhanClientId": Config.DHAN_CLIENT_ID
        })

        collection.insert_one(token_document)

        return {
            "status": True,
            "message": "Token generated and saved successfully",
            "accessToken": access_token,
            "expiryTime": expiry_time
        }

    except Exception as e:
        return {
            "status": False,
            "message": "Unexpected error occurred",
            "error": str(e)
        }
      
# ==========================
# MAIN EXECUTION        
        
totp = input("Enter 6-digit TOTP: ")

result = generate_and_store_token(totp)

print(result)    