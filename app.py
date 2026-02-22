from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException
from auth.token_service import generate_and_store_token
from services.profile_service import get_profile
from services.historic_service import get_historical_daily_data

import requests,os
from utils.smart_contract_service import smart_contract_lookup_service


from flask import Flask, request, jsonify, render_template
app = Flask(__name__)


# ==========================================================
# GLOBAL ERROR HANDLER
# ==========================================================
@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return jsonify({
            "status": False,
            "message": e.description
        }), e.code

    return jsonify({
        "status": False,
        "message": "Internal Server Error",
        "error": str(e)
    }), 500


@app.route("/profile-page")
def profile_page():
    result = get_profile()
    return render_template("profile.html", data=result)

@app.route("/historical-page", methods=["GET", "POST"])
def historical_page():
    result = None
    if request.method == "POST":
        result = get_historical_daily_data(
            security_id=request.form.get("security_id"),
            exchange_segment=request.form.get("exchange_segment"),
            instrument=request.form.get("instrument"),
            interval=request.form.get("interval"),
            start_date=request.form.get("start_date"),
            end_date=request.form.get("end_date"),
        )
    return render_template("historical.html", data=result)

@app.route("/lookup-page", methods=["GET", "POST"])
def lookup_page():
    result = None
    if request.method == "POST":
        query = request.form.get("query")
        result = smart_contract_lookup_service(query)
    return render_template("lookup.html", data=result)


# ==========================================================
# 🏠 HOME PAGE (HTML LOGIN PAGE)
# ==========================================================
@app.route("/", methods=["GET", "POST"])
def index():
    try:
        if request.method == "POST":
            totp = request.form.get("totp")

            if not totp:
                return render_template(
                    "index.html",
                    message="TOTP is required",
                    status_class="error"
                )

            result = generate_and_store_token(totp.strip())

            if result.get("status"):
                return render_template(
                    "index.html",
                    message="✅ Token generated successfully!",
                    status_class="success"
                )
            else:
                return render_template(
                    "index.html",
                    message=result.get("message", "Token generation failed"),
                    status_class="error"
                )

        return render_template("index.html")

    except Exception as e:
        return render_template(
            "index.html",
            message=str(e),
            status_class="error"
        )
        
# ==========================================================
# 1️⃣ LOGIN ROUTE (Supports JSON + Query Param)
# ==========================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    try:
        totp = None

        # GET → query param
        if request.method == "GET":
            totp = request.args.get("totp")

        # POST → JSON or query
        elif request.method == "POST":

            if request.args.get("totp"):
                totp = request.args.get("totp")

            elif request.is_json:
                data = request.get_json()
                if data:
                    totp = data.get("totp")

            elif request.form.get("totp"):
                totp = request.form.get("totp")

        if not totp:
            return jsonify({
                "status": False,
                "message": "TOTP is required"
            }), 400

        result = generate_and_store_token(str(totp).strip())
        return jsonify(result)

    except Exception as e:
        return jsonify({
            "status": False,
            "message": "Login failed",
            "error": str(e)
        }), 500
         
        
# ==========================================================
# 2️⃣ PROFILE ROUTE
# ==========================================================
@app.route("/profile", methods=["GET"])
def profile():
    try:
        result = get_profile()
        return jsonify(result)

    except Exception as e:
        return jsonify({
            "status": False,
            "message": "Profile fetch failed",
            "error": str(e)
        }), 500


# ==========================================================
# 3️⃣ HISTORICAL DATA ROUTE (GET + POST Supported)
# ==========================================================
@app.route("/historical", methods=["GET", "POST"])
def historical_data():
    try:
        data = {}

        # -----------------------------------------
        # GET → Query Parameters (Browser)
        # -----------------------------------------
        if request.method == "GET":
            data = request.args.to_dict()

        # -----------------------------------------
        # POST → JSON or Form
        # -----------------------------------------
        elif request.method == "POST":

            if request.is_json:
                data = request.get_json() or {}

            elif request.form:
                data = request.form.to_dict()

        if not data:
            return jsonify({
                "status": False,
                "message": "No input data provided"
            }), 400

        # ------------------------------
        # Required Fields
        # ------------------------------
        security_id = data.get("security_id")
        exchange_segment = data.get("exchange_segment")
        instrument = data.get("instrument")
        start_date = data.get("start_date",None)
        end_date = data.get("end_date",None)
        interval = data.get("interval",1)
        oi = data.get("oi", "false").lower() == "true"
        
        
        if not security_id:
            return jsonify({"status": False, "message": "security_id is required"}), 400

        if not exchange_segment:
            return jsonify({"status": False, "message": "exchange_segment is required"}), 400

        if not instrument:
            return jsonify({"status": False, "message": "instrument is required"}), 400

        # ------------------------------
        # Optional Fields Handling
        # ------------------------------


        result = get_historical_daily_data(
            security_id=str(security_id).strip(),
            exchange_segment=str(exchange_segment).strip(),
            instrument=str(instrument).strip(),
            interval=interval,
            oi=oi,
            start_date=start_date,
            end_date=end_date,
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({
            "status": False,
            "message": "Historical data fetch failed",
            "error": str(e)
        }), 500

# ==========================================================
# 4️⃣ SMART CONTRACT LOOKUP ROUTE (GET + POST)
# ==========================================================
@app.route("/lookup", methods=["GET", "POST"])
def smart_contract_lookup():
    try:
        # -------------------------------------------------
        # 🔹 HANDLE GET REQUEST (Query Params)
        # -------------------------------------------------
        if request.method == "GET":
            query = request.args.get("q")
            start_date = request.args.get("start_date")
            end_date = request.args.get("end_date")
            interval = int(request.args.get("interval", 1))

        # -------------------------------------------------
        # 🔹 HANDLE POST REQUEST (JSON Body)
        # -------------------------------------------------
        elif request.method == "POST":
            data = request.get_json()

            if not data:
                return jsonify({
                    "status": False,
                    "message": "Missing JSON body"
                }), 400

            query = data.get("q")
            start_date = data.get("start_date")
            end_date = data.get("end_date")
            interval = int(data.get("interval", 1))

        # -------------------------------------------------
        # 🔹 VALIDATION
        # -------------------------------------------------
        if not query:
            return jsonify({
                "status": False,
                "message": "Missing 'q' parameter"
            }), 400

        query = query.strip()

        # -------------------------------------------------
        # 🔥 CASE 1: If numeric → SECURITY_ID
        # -------------------------------------------------
        if query.isdigit():
            result = smart_contract_lookup_service(
                query,
                start_date=start_date,
                end_date=end_date,
                interval=interval
            )

        # -------------------------------------------------
        # 🔥 CASE 2: Symbol Lookup
        # -------------------------------------------------
        else:
            result = smart_contract_lookup_service(
                query,
                start_date=start_date,
                end_date=end_date,
                interval=interval
            )

        return jsonify(result)

    except Exception as e:
        return jsonify({
            "status": False,
            "message": "Lookup failed",
            "error": str(e)
        }), 500
        

# ==========================================================
# HEALTH CHECK ROUTE (Optional but Professional)
# ==========================================================
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": True,
        "message": "API is running"
    })


if __name__ == "__main__":
    app.run(debug=True)