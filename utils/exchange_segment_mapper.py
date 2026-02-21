# exchange_segment_mapper.py

from typing import Dict, Any


# ==========================================================
# EXCHANGE SEGMENT MAPPING
# ==========================================================
EXCHANGE_SEGMENT_MAP = {
    0: {
        "exchange_segment": "IDX_I",
        "exchange": "Index",
        "segment": "Index Value",
        "enum": 0
    },
    1: {
        "exchange_segment": "NSE_EQ",
        "exchange": "NSE",
        "segment": "Equity Cash",
        "enum": 1
    },
    2: {
        "exchange_segment": "NSE_FNO",
        "exchange": "NSE",
        "segment": "Futures & Options",
        "enum": 2
    },
    3: {
        "exchange_segment": "NSE_CURRENCY",
        "exchange": "NSE",
        "segment": "Currency",
        "enum": 3
    },
    4: {
        "exchange_segment": "BSE_EQ",
        "exchange": "BSE",
        "segment": "Equity Cash",
        "enum": 4
    },
    5: {
        "exchange_segment": "MCX_COMM",
        "exchange": "MCX",
        "segment": "Commodity",
        "enum": 5
    },
    7: {
        "exchange_segment": "BSE_CURRENCY",
        "exchange": "BSE",
        "segment": "Currency",
        "enum": 7
    },
    8: {
        "exchange_segment": "BSE_FNO",
        "exchange": "BSE",
        "segment": "Futures & Options",
        "enum": 8
    }
}


# ==========================================================
# GET EXCHANGE SEGMENT BY ENUM
# ==========================================================
def get_exchange_segment(index: int) -> Dict[str, Any]:
    """
    Returns exchange segment details based on enum index.
    """

    if index not in EXCHANGE_SEGMENT_MAP:
        return {
            "status": "error",
            "message": f"Invalid exchange segment index: {index}"
        }

    return {
        "status": "success",
        "data": EXCHANGE_SEGMENT_MAP[index]
    }


# # ==========================================================
# # TESTING
# # ==========================================================
# if __name__ == "__main__":
#     print(get_exchange_segment(2))