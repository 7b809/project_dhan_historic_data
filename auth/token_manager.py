# auth/token_manager.py

from datetime import datetime
from config import Config
from database.mongo import get_collection


def get_valid_access_token():
    """
    Returns access token only if valid.
    If expired → ask user to generate new token.
    """

    collection = get_collection()

    token_doc = collection.find_one({
        "dhanClientId": Config.DHAN_CLIENT_ID
    })

    if not token_doc:
        return {
            "status": False,
            "message": "No token found. Please login."
        }

    access_token = token_doc.get("accessToken")
    expiry_time_str = token_doc.get("expiryTime")

    if not access_token or not expiry_time_str:
        return {
            "status": False,
            "message": "Invalid token data. Please login again."
        }

    expiry_time = datetime.fromisoformat(expiry_time_str)
    now = datetime.utcnow()

    # ❌ Token expired
    if now >= expiry_time:
        return {
            "status": False,
            "message": "Token expired. Please generate new one."
        }

    # ✅ Token valid
    return {
        "status": True,
        "accessToken": access_token
    }