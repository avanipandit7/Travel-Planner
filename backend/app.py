"""
app.py — plain REST backend for the Mumbai trip planner.

No chatbot, no LLM, no agent loop. Routes call tools.py directly. This is
the "does the core app work" phase — agent.py / tool_schemas.py / run_tests.py
plug in later as an alternate route once the chatbot layer is added; the
tools.py functions underneath don't change either way.

Routes:
  POST /api/transport   -> { origin, date }
  POST /api/hotels      -> { nights, max_price_per_night? }
  POST /api/activities  -> { interests }
  POST /api/plan        -> { origin, date, nights, interests, budget, max_price_per_night? }
                            runs all three searches + calculate_budget, one combined result

Destination is always Mumbai in this scope — never accepted as input.

Run:
  pip install -r requirements.txt
  python app.py            # serves on http://127.0.0.1:5000
"""

from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS

from tools import search_transport, search_hotels, search_activities, calculate_budget
from input_handler import ALLOWED_INTERESTS

app = Flask(__name__)
CORS(app)  # dev-friendly; tighten origins before deploying

DESTINATION = "Mumbai"  # fixed for this scope — not accepted as user input


# --------------------------- validation helpers ---------------------------

def validation_error(errors):
    return jsonify({"errors": errors}), 400


def require_origin(body, errors):
    origin = body.get("origin")
    if not isinstance(origin, str) or not origin.strip():
        errors.append({"field": "origin", "message": "This field is required."})
        return None
    return origin.strip()


def require_date(body, errors):
    date_str = body.get("date")
    if not isinstance(date_str, str) or not date_str:
        errors.append({"field": "date", "message": "This field is required (format YYYY-MM-DD)."})
        return None
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        errors.append({"field": "date", "message": "Must match format YYYY-MM-DD, e.g. 2026-09-14."})
        return None
    return date_str


def require_nights(body, errors):
    nights = body.get("nights")
    try:
        nights = int(nights)
    except (TypeError, ValueError):
        errors.append({"field": "nights", "message": "Must be a whole number."})
        return None
    if nights <= 0:
        errors.append({"field": "nights", "message": "Must be greater than 0."})
        return None
    return nights


def require_budget(body, errors):
    budget = body.get("budget")
    try:
        budget = float(budget)
    except (TypeError, ValueError):
        errors.append({"field": "budget", "message": "Must be a number."})
        return None
    if budget <= 0:
        errors.append({"field": "budget", "message": "Must be greater than 0."})
        return None
    return budget


def require_interests(body, errors):
    interests = body.get("interests")
    if not isinstance(interests, list) or not interests:
        errors.append({"field": "interests", "message": "Must be a non-empty list of tags."})
        return None
    invalid = [t for t in interests if t not in ALLOWED_INTERESTS]
    if invalid:
        errors.append(
            {
                "field": "interests",
                "message": f"Unrecognized tag(s): {', '.join(invalid)}. Allowed: {', '.join(sorted(ALLOWED_INTERESTS))}.",
            }
        )
        return None
    return interests


def optional_max_price(body, errors):
    value = body.get("max_price_per_night")
    if value is None:
        return None
    try:
        value = float(value)
    except (TypeError, ValueError):
        errors.append({"field": "max_price_per_night", "message": "Must be a number if provided."})
        return None
    return value


# --------------------------------- routes ---------------------------------

@app.post("/api/transport")
def transport():
    body = request.get_json(silent=True) or {}
    errors = []
    origin = require_origin(body, errors)
    date = require_date(body, errors)
    if errors:
        return validation_error(errors)

    results = search_transport(origin=origin, destination=DESTINATION, date=date)
    return jsonify({"results": results})


@app.post("/api/hotels")
def hotels():
    body = request.get_json(silent=True) or {}
    errors = []
    nights = require_nights(body, errors)
    max_price = optional_max_price(body, errors)
    if errors:
        return validation_error(errors)

    results = search_hotels(destination=DESTINATION, nights=nights, max_price_per_night=max_price)
    return jsonify({"results": results})


@app.post("/api/activities")
def activities():
    body = request.get_json(silent=True) or {}
    errors = []
    interests = require_interests(body, errors)
    if errors:
        return validation_error(errors)

    results = search_activities(destination=DESTINATION, interests=interests)
    return jsonify({"results": results})


@app.post("/api/plan")
def plan():
    """Runs transport + hotels + activities + budget check in one call."""
    body = request.get_json(silent=True) or {}
    errors = []
    origin = require_origin(body, errors)
    date = require_date(body, errors)
    nights = require_nights(body, errors)
    interests = require_interests(body, errors)
    budget = require_budget(body, errors)
    max_price = optional_max_price(body, errors)
    if errors:
        return validation_error(errors)

    transport_options = search_transport(origin=origin, destination=DESTINATION, date=date)
    hotel_options = search_hotels(destination=DESTINATION, nights=nights, max_price_per_night=max_price)
    activity_options = search_activities(destination=DESTINATION, interests=interests)

    # Pick the cheapest valid option from each to check against budget.
    # (A later, smarter version — or the agent — can choose more deliberately.)
    valid_transport = [t for t in transport_options if "cost" in t]
    valid_hotels = [h for h in hotel_options if "price_per_night" in h]
    valid_activities = [a for a in activity_options if "cost" in a]

    transport_cost = min((t["cost"] for t in valid_transport), default=0)
    hotel_cost = (min((h["price_per_night"] for h in valid_hotels), default=0)) * nights
    activities_cost = sum(a["cost"] for a in valid_activities)

    budget_check = calculate_budget(
        transport_cost=transport_cost,
        hotel_cost=hotel_cost,
        activities_cost=activities_cost,
        total_budget=budget,
    )

    return jsonify(
        {
            "transport": transport_options,
            "hotels": hotel_options,
            "activities": activity_options,
            "budget_check": budget_check,
        }
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)