"""
Web server: lets the React frontend talk to the Python agent.

    React (browser)  --POST /api/plan-->  this file  -->  agent.run_agent()  -->  Gemini + tools

Run it (from the backend/ folder, with the venv active):
    python server.py

NOTE: validation lives here for now. When your partner finishes input_handler.py,
swap validate_trip_request() for their version — the rest of this file won't change.
"""
from datetime import date

from flask import Flask, jsonify, request
from google.genai import errors as genai_errors

from agent import run_agent

app = Flask(__name__)

VALID_INTERESTS = {"food", "culture", "adventure", "nature", "nightlife", "shopping"}
MIN_NIGHTS = 1
MAX_NIGHTS = 10


def validate_trip_request(data):
    """
    Checks the form data coming from the frontend.
    Returns (clean_dict, None) if everything is fine,
    or (None, "message explaining what's wrong") if not.
    """
    if not isinstance(data, dict):
        return None, "Request body must be JSON."

    origin = str(data.get("origin", "")).strip()
    if not origin:
        return None, "Please choose an origin city."

    try:
        start = date.fromisoformat(str(data.get("start_date", "")))
        end = date.fromisoformat(str(data.get("end_date", "")))
    except ValueError:
        return None, "Dates must be in YYYY-MM-DD format."

    nights = (end - start).days
    if nights < MIN_NIGHTS:
        return None, "The end date must be after the start date."
    if nights > MAX_NIGHTS:
        return None, f"Trips can be at most {MAX_NIGHTS} nights."

    try:
        budget = float(data.get("budget"))
    except (TypeError, ValueError):
        return None, "Budget must be a number."
    if budget <= 0:
        return None, "Budget must be greater than zero."

    interests = data.get("interests")
    if not isinstance(interests, list) or not interests:
        return None, "Pick at least one interest."
    interests = [str(i).strip().lower() for i in interests]
    bad = [i for i in interests if i not in VALID_INTERESTS]
    if bad:
        return None, f"Unknown interest(s): {', '.join(bad)}."

    return {
        "origin": origin,
        "start": start,
        "end": end,
        "nights": nights,
        "budget": budget,
        "interests": interests,
    }, None


def build_request_text(trip):
    """Turns the clean form data into the sentence the agent reads."""
    budget = int(trip["budget"]) if trip["budget"] == int(trip["budget"]) else trip["budget"]
    night_word = "night" if trip["nights"] == 1 else "nights"
    interests = " and ".join(trip["interests"]) if len(trip["interests"]) <= 2 else (
        ", ".join(trip["interests"][:-1]) + " and " + trip["interests"][-1]
    )
    return (
        f"Plan a trip from {trip['origin']} to Mumbai, "
        f"{trip['start'].isoformat()} to {trip['end'].isoformat()} "
        f"({trip['nights']} {night_word}), budget {budget} INR, "
        f"interested in {interests}."
    )


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/plan")
def plan():
    trip, problem = validate_trip_request(request.get_json(silent=True))
    if problem:
        return jsonify({"error": problem}), 400

    request_text = build_request_text(trip)
    print(f"\n[server] {request_text}")

    try:
        result = run_agent(request_text, verbose=True)
    except genai_errors.APIError as e:
        # e.code is the HTTP status Google returned (429 = daily/minute quota used up)
        if e.code == 429:
            return jsonify({
                "error": "The Gemini free-tier quota is used up for now. "
                         "Wait a while (daily limits reset overnight) or switch MODEL in agent.py."
            }), 429
        print(f"[server] Gemini API error: {e}")
        return jsonify({"error": f"Gemini API error ({e.code}): {e.message}"}), 502
    except Exception as e:
        print(f"[server] Unexpected error: {type(e).__name__}: {e}")
        return jsonify({"error": f"Something went wrong on the server: {type(e).__name__}: {e}"}), 500

    result["request_text"] = request_text
    return jsonify(result)


if __name__ == "__main__":
    # 127.0.0.1 (not "localhost") on purpose — see vite.config.js for why
    app.run(host="127.0.0.1", port=5000, debug=False)