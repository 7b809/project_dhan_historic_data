import requests
from datetime import datetime
from config import Config
from database.mongo import get_collection


def generate_and_store_token(totp: str) -> dict:
    try:
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
            return {"status": False, "message": response.text}

        data = response.json()

        access_token = data.get("accessToken")
        expiry_time = data.get("expiryTime")

        if not access_token:
            return {"status": False, "message": "Access token missing"}

        collection = get_collection()

        collection.delete_many({
            "dhanClientId": Config.DHAN_CLIENT_ID
        })

        collection.insert_one({
            "dhanClientId": Config.DHAN_CLIENT_ID,
            "accessToken": access_token,
            "expiryTime": expiry_time,
            "createdAt": datetime.utcnow()
        })

        return {
            "status": True,
            "message": "Token generated successfully",
            "accessToken": access_token,
            "expiryTime": expiry_time
        }

    except Exception as e:
        return {"status": False, "message": str(e)}