from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException
from auth.token_service import generate_and_store_token
from services.profile_service import get_profile
from services.historic_service import get_historical_daily_data

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
# 3️⃣ HISTORICAL DATA ROUTE
# ==========================================================
@app.route("/historical", methods=["POST"])
def historical_data():
    try:
        if not request.is_json:
            return jsonify({
                "status": False,
                "message": "Request must be JSON"
            }), 400

        data = request.get_json()

        if not data:
            return jsonify({
                "status": False,
                "message": "Request body cannot be empty"
            }), 400

        security_id = data.get("security_id")
        exchange_segment = data.get("exchange_segment")
        instrument = data.get("instrument")

        # Required fields validation
        if not security_id:
            return jsonify({
                "status": False,
                "message": "security_id is required"
            }), 400

        if not exchange_segment:
            return jsonify({
                "status": False,
                "message": "exchange_segment is required"
            }), 400

        if not instrument:
            return jsonify({
                "status": False,
                "message": "instrument is required"
            }), 400

        result = get_historical_daily_data(
            security_id=str(security_id).strip(),
            exchange_segment=str(exchange_segment).strip(),
            instrument=str(instrument).strip(),
            interval=data.get("interval", 1),
            oi=data.get("oi", False),
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({
            "status": False,
            "message": "Historical data fetch failed",
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