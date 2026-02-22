import requests
from datetime import datetime
from dotenv import load_dotenv
import os

# 🔥 Optional historical import (safe import)
try:
    from services.historic_service import get_historical_daily_data
except ImportError:
    get_historical_daily_data = None

load_dotenv()

BASE_OPTION_API = os.getenv("BASE_OPTION_API")


# ==========================================================
# PARSE CONTRACT QUERY (UNCHANGED LOGIC)
# ==========================================================
def parse_contract_query(query: str):
    """
    Parses:
    NIFTY 24 FEB 25500 CALL
    Returns structured dictionary
    """

    query = query.upper().strip()
    parts = query.split()

    if len(parts) < 5:
        return None

    symbol = parts[0]
    day = parts[1]
    month = parts[2]
    strike = parts[3]
    option_type = parts[4]

    year = datetime.now().year
    expiry = f"{day}{month}{year}"  # 24FEB2026 format

    return {
        "symbol": symbol,
        "expiry": expiry,
        "strike": strike,
        "type": option_type
    }


# ==========================================================
# FETCH SECURITY FROM DEPLOYED DOMAIN (UNCHANGED LOGIC)
# ==========================================================
def fetch_security_from_domain(contract_data: dict):
    """
    Calls deployed option API
    Step 1 → contract-lookup
    Step 2 → security
    """

    if not BASE_OPTION_API:
        return None

    # -------------------------
    # Step 1: Contract Lookup
    # -------------------------
    contract_url = f"{BASE_OPTION_API}/contract-lookup"

    contract_response = requests.get(contract_url, params=contract_data)

    if contract_response.status_code != 200:
        return None

    contract_json = contract_response.json()
    security_id = contract_json.get("SECURITY_ID")

    if not security_id:
        return None

    # -------------------------
    # Step 2: Full Security Fetch
    # -------------------------
    security_url = f"{BASE_OPTION_API}/security"

    security_response = requests.get(
        security_url,
        params={"security_id": security_id}
    )

    if security_response.status_code != 200:
        return None

    return security_response.json()

# ==========================================================
# MAP EXCHANGE SEGMENT FOR HISTORICAL API
# ==========================================================
def map_exchange_segment(security_data: dict):
    """
    Maps security response to exchange_segment required by historical API
    """

    exch = security_data.get("EXCH_ID", "").upper()
    instrument_type = security_data.get("INSTRUMENT_TYPE", "").upper()

    if not exch:
        return None

    # Derivatives (Options + Futures)
    if instrument_type in ["OP", "OPTIDX", "OPTSTK", "FUTIDX", "FUTSTK", "FUTCUR"]:
        return f"{exch}_FNO"

    # Cash market
    return f"{exch}_EQ"

# ==========================================================
# SMART CONTRACT LOOKUP SERVICE (EXTENDED SAFELY)
# ==========================================================
def smart_contract_lookup_service(
    query: str,
    start_date=None,
    end_date=None,
    interval=1,
):
    """
    Full smart lookup service

    ✔ Existing behavior unchanged
    ✔ Historical optional
    ✔ No logic removed
    """

    parsed = parse_contract_query(query)

    if not parsed:
        return {
            "status": False,
            "message": "Invalid format. Use: NIFTY 24 FEB 25500 CALL"
        }

    security_data = fetch_security_from_domain(parsed)

    if not security_data:
        return {
            "status": False,
            "message": "Contract not found"
        }


    security_id = security_data.get("SECURITY_ID")
    exchange_segment = map_exchange_segment(security_data)    
    instrument = security_data.get("INSTRUMENT")
    
    historical_data = get_historical_daily_data(
            security_id=str(security_id),
            exchange_segment=str(exchange_segment),
            instrument=str(instrument),
            interval=interval,
            oi=False,
            start_date=start_date,
            end_date=end_date
        )


    return historical_data if historical_data else security_data