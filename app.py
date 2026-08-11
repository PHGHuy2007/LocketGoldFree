from flask import Flask, render_template, request, jsonify, send_from_directory
from auth import Auth
from api import LocketAPI
from history_store import HistoryStore
import json
import requests
import threading
import uuid
from datetime import datetime
import dotenv
import os

app = Flask(__name__)

dotenv.load_dotenv()

# Initialize API and Auth
subscription_ids = [
    "locket_1600_1y",
    "locket_199_1m",
    "locket_199_1m_only",
    "locket_3600_1y",
    "locket_399_1m_only",
]

auth = Auth(os.getenv("EMAIL"), os.getenv("PASSWORD"))
try:
    token = auth.get_token()
    api = LocketAPI(token)
except Exception as e:
    print(f"Error initializing API: {e}")
    api = None

history_store = HistoryStore()

def refresh_api_token():
    global api
    try:
        print("Refreshing API token...")
        new_token = auth.create_token()
        api = LocketAPI(new_token)
        print("API token refreshed successfully.")
        return True
    except Exception as e:
        print(f"Failed to refresh API token: {e}")
        return False

def _process_request(client_id, username):
    """Process a single restore purchase request. This is the core logic."""
    try:
        print(f"Processing restore for: {username} ({client_id})")

        # User lookup
        try:
            account_info = api.getUserByUsername(username)
        except Exception as e:
            if "401" in str(e) or "Unauthenticated" in str(e):
                print(f"Creating new token because of {e}")
                if refresh_api_token():
                    account_info = api.getUserByUsername(username)
                else:
                    raise e
            else:
                raise e

        if not account_info or "result" not in account_info:
            raise Exception("User not found or API error")

        user_data = account_info.get("result", {}).get("data")
        if not user_data:
            raise Exception("User data not found")

        uid_target = user_data.get("uid")
        if not uid_target:
            raise Exception("UID not found for user")

        # Restore purchase
        try:
            restore_result = api.restorePurchase(uid_target)
        except Exception as e:
            if "401" in str(e) or "Unauthenticated" in str(e):
                print(f"Creating new token because of {e}")
                if refresh_api_token():
                    restore_result = api.restorePurchase(uid_target)
                else:
                    raise e
            else:
                raise e

        entitlements = restore_result.get("subscriber", {}).get("entitlements", {})
        gold_entitlement = entitlements.get("Gold", {})

        if gold_entitlement.get("product_identifier") in subscription_ids:
            product_id = gold_entitlement.get("product_identifier")
            send_telegram_notification(username, uid_target, product_id, restore_result)

            success_message = f"Purchase {product_id} for {username} successfully!"
            history_store.update_request(
                client_id,
                "completed",
                success_message,
                uid=uid_target,
                product_id=product_id,
            )
        else:
            raise Exception(
                f"Restore purchase failed. Gold entitlement not found for {username}."
            )

    except Exception as e:
        error_message = str(e)
        print(f"Error processing request for {client_id}: {error_message}")
        try:
            history_store.update_request(client_id, "error", error_message)
        except Exception as history_error:
            print(f"Failed to update history entry: {history_error}")

@app.route("/download-config")
def download_config():
    return send_from_directory(
        "static", "locket.mobileconfig", mimetype="application/x-apple-aspen-config"
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/get-user-info", methods=["POST"])
def get_user_info():
    if not api:
        return jsonify(
            {"success": False, "msg": "API not initialized. Check server logs."}
        ), 500

    data = request.json
    username = data.get("username")

    if not username:
        return jsonify({"success": False, "msg": "Username is required"}), 400

    try:
        # User lookup
        print(f"Looking up user: {username}")
        try:
            account_info = api.getUserByUsername(username)
        except Exception as e:
            if "401" in str(e) or "Unauthenticated" in str(e):
                print(f"Creating new token because of {e}")
                if refresh_api_token():
                    account_info = api.getUserByUsername(username)
                else:
                    raise e
            else:
                raise e

        # Check if we got a valid response structure
        if not account_info or "result" not in account_info:
            return jsonify(
                {"success": False, "msg": "User not found or API error"}
            ), 404

        user_data = account_info.get("result", {}).get("data")
        if not user_data:
            return jsonify({"success": False, "msg": "User data not found"}), 404

        # Extract relevant user information
        user_info = {
            "uid": user_data.get("uid"),
            "username": user_data.get("username"),
            "first_name": user_data.get("first_name", ""),
            "last_name": user_data.get("last_name", ""),
            "profile_picture_url": user_data.get("profile_picture_url", ""),
        }

        return jsonify({"success": True, "data": user_info})

    except Exception as e:
        print(f"Error in get user info: {e}")
        return jsonify({"success": False, "msg": f"An error occurred: {str(e)}"}), 500


def send_telegram_notification(username, uid, product_id, raw_json):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if bot_token == "" or chat_id == "":
        print("Telegram notification skipped: Token or Chat ID not set.")
        return
    import time
    subscription_info = json.dumps(
        raw_json.get("subscriber", {}).get("entitlements", {}).get("Gold", {}), indent=2
    )

    message = f"✅ <b>Locket Gold Unlocked!</b>\n\n👤 <b>User:</b> {username} ({uid})\n⏰ <b>Time:</b> {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n<b>Subscription Info:</b>\n<pre>{subscription_info}</pre>"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"    
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}

    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Failed to send Telegram notification: {e}")


@app.route("/api/restore", methods=["POST"])
def restore_purchase():
    """Add request to queue and return client_id for tracking"""
    if not api:
        return jsonify(
            {"success": False, "msg": "API not initialized. Check server logs."}
        ), 500

    data = request.json
    username = data.get("username")

    if not username:
        return jsonify({"success": False, "msg": "Username is required"}), 400

    try:
        client_id = str(uuid.uuid4())
        history_store.create_request(client_id, username)

        # Provide an initial estimate
        waiting_jobs = history_store.count_jobs("waiting")
        estimated_time = waiting_jobs * 35  # Estimate 35s per job

        return jsonify(
            {
                "success": True,
                "client_id": client_id,
                "position": waiting_jobs,
                "total_queue": waiting_jobs,
                "estimated_time": estimated_time,
            }
        )

    except Exception as e:
        print(f"Error adding to queue: {e}")
        return jsonify({"success": False, "msg": f"An error occurred: {str(e)}"}), 500


@app.route("/api/queue/status", methods=["POST"])
def queue_status():
    """Get current queue status for a client"""
    data = request.json
    client_id = data.get("client_id")

    if not client_id:
        return jsonify({"success": False, "msg": "client_id is required"}), 400

    request_data = history_store.get_request(client_id)

    if not request_data:
        return jsonify({"success": False, "msg": "Client ID not found"}), 404

    # Estimate position and wait time
    position = 0
    total_queue = 0
    estimated_time = 0

    if request_data["status"] == "waiting":
        # This is a simplified estimation.
        total_queue = history_store.count_jobs("waiting")
        position = total_queue # A rough approximation
        estimated_time = total_queue * 35 # ~35s per job

    return jsonify({
        "success": True,
        "client_id": client_id,
        "status": request_data["status"],
        "position": position,
        "total_queue": total_queue,
        "estimated_time": estimated_time,
        "result": {"success": True, "msg": request_data["message"]} if request_data["status"] == "completed" else None,
        "error": request_data["message"] if request_data["status"] == "error" else None,
    })


@app.route("/api/history", methods=["GET"])
def history():
    """Return recent public restore request history."""
    try:
        limit = request.args.get("limit", 20)
        return jsonify({"success": True, "data": history_store.recent(limit)})
    except Exception as e:
        print(f"Error loading history: {e}")
        return jsonify({"success": False, "msg": "Could not load history"}), 500

@app.route("/api/cron/process-job", methods=["GET"])
def process_job():
    # Secure this endpoint with a secret from environment variables
    auth_header = request.headers.get('Authorization')
    cron_secret = os.getenv("CRON_SECRET")
    if not cron_secret or auth_header != f"Bearer {cron_secret}":
        return jsonify({"success": False, "msg": "Unauthorized"}), 401

    # Check if a job is already processing to avoid overlap on Vercel
    if history_store.count_jobs("processing") > 0:
        return jsonify({"success": True, "msg": "A job is already processing."}), 200

    job = history_store.fetch_and_lock_job()
    if not job:
        return jsonify({"success": True, "msg": "No jobs to process."}), 200

    # The job is now 'processing'. The actual work is done here.
    _process_request(job["client_id"], job["username"])

    return jsonify({"success": True, "msg": f"Processed job for {job['username']}."}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
