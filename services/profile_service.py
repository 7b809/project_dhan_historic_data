import requests
from config import Config
from auth.token_manager import get_valid_access_token


def get_profile():
    """
    Fetch Dhan profile.
    Automatically handles:
    - Token expiry check
    - Auto renewal if < 1 hour remaining
    """

    # ==========================================
    # GET VALID TOKEN (AUTO RENEW LOGIC INSIDE)
    # ==========================================
    token_data = get_valid_access_token()

    if not token_data.get("status"):
        return token_data  # Login required or renewal failed

    access_token = token_data["accessToken"]

    # ==========================================
    # CALL DHAN PROFILE API
    # ==========================================
    headers = {
        "access-token": access_token
    }

    try:
        response = requests.get(
            Config.PROFILE_URL,
            headers=headers,
            timeout=15
        )

        if response.status_code != 200:
            return {
                "status": False,
                "message": "Profile fetch failed",
                "error": response.text
            }

        return {
            "status": True,
            "data": response.json()
        }

    except Exception as e:
        return {
            "status": False,
            "message": "Unexpected error occurred",
            "error": str(e)
        }