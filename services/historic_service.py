import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from config import Config
from auth.token_manager import get_valid_access_token
from zoneinfo import ZoneInfo  # ✅ Added for IST timezone


# ==========================================================
# COMMON ERROR RESPONSE FORMATTER
# ==========================================================
def _error(message: str) -> Dict[str, Any]:
    return {
        "status": "error",
        "message": message
    }


# ==========================================================
# VALIDATE DATETIME FORMAT
# ==========================================================
def _validate_datetime_format(date_str: str, is_start: bool) -> str:
    """
    Accepts:
    - YYYY-MM-DD HH:MM:SS
    - DD-MM-YYYY

    Returns formatted string: YYYY-MM-DD HH:MM:SS
    """

    try:
        # Case 1: Full datetime already provided
        datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return date_str

    except ValueError:
        try:
            # Case 2: Only date provided in DD-MM-YYYY
            base_date = datetime.strptime(date_str, "%d-%m-%Y")

            if is_start:
                base_date = base_date.replace(hour=9, minute=15, second=0)
            else:
                base_date = base_date.replace(hour=13, minute=31, second=0)

            return base_date.strftime("%Y-%m-%d %H:%M:%S")

        except ValueError:
            raise ValueError(
                "Date must be either YYYY-MM-DD HH:MM:SS or DD-MM-YYYY"
            )
# ==========================================================
# GET LAST TRADING DAY (WEEKDAY ONLY) — IST SAFE
# ==========================================================
def _get_last_trading_day() -> datetime:
    # ✅ Force IST timezone
    today = datetime.now(ZoneInfo("Asia/Kolkata"))

    if today.weekday() == 5:  # Saturday
        return today - timedelta(days=1)

    if today.weekday() == 6:  # Sunday
        return today - timedelta(days=2)

    return today


# ==========================================================
# TRANSFORM ARRAY RESPONSE TO DATE → TIME → CANDLE FORMAT
# ==========================================================
def _transform_intraday_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        formatted_data = {}

        opens = raw_data.get("open", [])
        highs = raw_data.get("high", [])
        lows = raw_data.get("low", [])
        closes = raw_data.get("close", [])
        volumes = raw_data.get("volume", [])
        timestamps = raw_data.get("timestamp", [])

        for i in range(len(timestamps)):
            ts = timestamps[i]

            # ✅ Force IST timezone (server-independent)
            dt = datetime.fromtimestamp(ts, tz=ZoneInfo("Asia/Kolkata"))

            date_str = dt.strftime("%d-%m-%Y")
            time_str = dt.strftime("%H:%M")

            if date_str not in formatted_data:
                formatted_data[date_str] = {}

            formatted_data[date_str][time_str] = {
                "o": opens[i],
                "h": highs[i],
                "l": lows[i],
                "c": closes[i],
                "v": volumes[i]
            }

        return formatted_data

    except Exception as e:
        return {"error": f"Transformation failed: {str(e)}"}


# ==========================================================
# HISTORICAL DAILY DATA
# ==========================================================
def get_historical_daily_data(
    security_id: str,
    exchange_segment: str,
    instrument: str,
    interval: int = 1,
    oi: bool = False,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:

    try:
        if not security_id:
            return _error("security_id is required")

        if not exchange_segment:
            return _error("exchange_segment is required")

        if not instrument:
            return _error("instrument is required")

        # ==================================================
        # 🔐 GET VALID TOKEN (AUTO RENEW LOGIC)
        # ==================================================
        token_data = get_valid_access_token()

        if not token_data.get("status"):
            return token_data  # Login required or renew failed

        access_token = token_data["accessToken"]

        # --------------------------------------------------
        # DEFAULT DATETIME HANDLING (30 DAYS)
        # --------------------------------------------------
        if not start_date or not end_date:
            today = _get_last_trading_day()

            # End time fixed to 13:31:00 (unchanged logic)
            end_datetime = today.replace(hour=13, minute=31, second=0)

            # Start time 30 days ago at 09:15:00
            start_base = today - timedelta(days=30)
            start_datetime = start_base.replace(hour=9, minute=15, second=0)

            start_date = start_datetime.strftime("%Y-%m-%d %H:%M:%S")
            end_date = end_datetime.strftime("%Y-%m-%d %H:%M:%S")

        # Validate datetime format
        # ==================================================
        # VALIDATE / FORMAT USER PROVIDED DATES
        # ==================================================

        start_date = _validate_datetime_format(start_date, is_start=True)
        end_date = _validate_datetime_format(end_date, is_start=False)

        # --------------------------------------------------
        # API PAYLOAD
        # --------------------------------------------------
        payload = {
            "securityId": security_id,
            "exchangeSegment": exchange_segment,
            "instrument": instrument,
            "fromDate": start_date,
            "toDate": end_date,
            "oi": oi,
            "interval": interval
        }

        headers = {
            "access-token": access_token,
            "Content-Type": "application/json"
        }

        response = requests.post(
            Config.DHAN_HISTORICAL_API_URL,
            json=payload,
            headers=headers
        )

        if response.status_code != 200:
            return _error(f"Dhan API Error: {response.text}")

        response_data = response.json()
        return _transform_intraday_data(response_data)

    except Exception as e:
        return _error(str(e))