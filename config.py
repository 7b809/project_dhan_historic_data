import os
from dotenv import load_dotenv
from dhanhq import dhanhq
# Load env only once
load_dotenv()

class Config:
    # ==========================
    # DHAN CONFIG
    # ==========================
    DHAN_CLIENT_ID = os.getenv("DHAN_CLIENT_ID")
    DHAN_PIN = os.getenv("DHAN_PIN")
    DHAN_ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")    
    DHAN_INSTANCE = dhanhq(
        client_id=DHAN_CLIENT_ID,
        access_token=DHAN_ACCESS_TOKEN
    )
    # ==========================
    # MONGODB CONFIG
    # ==========================
    MONGO_URL = os.getenv("MONGO_URL")
    DB_NAME = os.getenv("DB_NAME")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME")

    # ==========================
    # DHAN ENDPOINTS
    # ==========================
    GENERATE_TOKEN_URL = "https://auth.dhan.co/app/generateAccessToken"
    PROFILE_URL = "https://api.dhan.co/v2/profile"
    DHAN_HISTORICAL_API_URL = "https://api.dhan.co/v2/charts/intraday"