"""
input_handler.py — validates a raw trip request before it's allowed to touch
the conversation engine, agentic tool calls, or the database.

Collects ALL validation errors in one pass (not fail-fast) so the frontend
can show every problem at once instead of one round-trip per fix.
"""

from datetime import date, datetime

ALLOWED_INTERESTS = {"food", "culture", "adventure", "nature", "nightlife", "shopping"}

DATE_FORMAT = "%Y-%m-%d"  # expects ISO format, e.g. "2026-09-14"


class TripRequestError(Exception):
    """Raised when a trip request fails validation.

    .errors is a list of {"field": str, "message": str} dicts, so the API
    layer can return them directly as JSON to the frontend.
    """

    def __init__(self, errors: list[dict]):
        self.errors = errors
        super().__init__(f"{len(errors)} validation error(s): {errors}")


def _parse_date(value, field_name: str, errors: list) -> date | None:
    if value is None or value == "":
        errors.append({"field": field_name, "message": "This field is required."})
        return None
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        errors.append({"field": field_name, "message": "Must be a date string (YYYY-MM-DD)."})
        return None
    try:
        return datetime.strptime(value, DATE_FORMAT).date()
    except ValueError:
        errors.append({"field": field_name, "message": f"Must match format {DATE_FORMAT}, e.g. 2026-09-14."})
        return None


def _parse_budget(value, errors: list) -> float | None:
    if value is None or value == "":
        errors.append({"field": "budget", "message": "This field is required."})
        return None
    try:
        budget = float(value)
    except (TypeError, ValueError):
        errors.append({"field": "budget", "message": "Must be a number."})
        return None
    if budget <= 0:
        errors.append({"field": "budget", "message": "Must be greater than 0."})
        return None
    return budget


def _parse_interests(value, errors: list) -> list[str]:
    if value is None:
        errors.append({"field": "interests", "message": "This field is required."})
        return []
    if not isinstance(value, (list, tuple, set)):
        errors.append({"field": "interests", "message": "Must be a list of tags."})
        return []

    cleaned = []
    invalid = []
    for tag in value:
        if not isinstance(tag, str):
            invalid.append(str(tag))
            continue
        normalized = tag.strip().lower()
        if normalized not in ALLOWED_INTERESTS:
            invalid.append(tag)
        else:
            cleaned.append(normalized)

    if invalid:
        errors.append(
            {
                "field": "interests",
                "message": (
                    f"Unrecognized tag(s): {', '.join(str(t) for t in invalid)}. "
                    f"Allowed: {', '.join(sorted(ALLOWED_INTERESTS))}."
                ),
            }
        )
    if not cleaned and not invalid:
        errors.append({"field": "interests", "message": "Pick at least one interest."})

    # De-duplicate while preserving order
    seen = set()
    deduped = []
    for tag in cleaned:
        if tag not in seen:
            seen.add(tag)
            deduped.append(tag)
    return deduped


def parse_trip_request(raw: dict) -> dict:
    """Validate a raw trip request dict (e.g. from request.get_json()).

    Checks:
      - start_date and end_date are valid dates, end_date is strictly after start_date
      - budget is numeric and > 0
      - interests only contain the 6 fixed tags (food, culture, adventure,
        nature, nightlife, shopping) — unrecognized tags are rejected, not
        silently dropped

    Returns a cleaned dict on success:
        {
            "start_date": date,
            "end_date": date,
            "budget": float,
            "currency": str,      # defaults to "USD" if omitted
            "interests": list[str],
        }

    Raises TripRequestError (with .errors) if anything is invalid.
    """
    if not isinstance(raw, dict):
        raise TripRequestError([{"field": "_root", "message": "Request body must be a JSON object."}])

    errors: list[dict] = []

    start_date = _parse_date(raw.get("start_date"), "start_date", errors)
    end_date = _parse_date(raw.get("end_date"), "end_date", errors)

    if start_date is not None and end_date is not None and end_date <= start_date:
        errors.append({"field": "end_date", "message": "Must be after start_date."})

    budget = _parse_budget(raw.get("budget"), errors)

    currency = raw.get("currency") or "USD"
    if not isinstance(currency, str) or len(currency.strip()) != 3:
        errors.append({"field": "currency", "message": "Must be a 3-letter currency code, e.g. USD."})
        currency = None
    else:
        currency = currency.strip().upper()

    interests = _parse_interests(raw.get("interests"), errors)

    if errors:
        raise TripRequestError(errors)

    return {
        "start_date": start_date,
        "end_date": end_date,
        "budget": budget,
        "currency": currency,
        "interests": interests,
    }


if __name__ == "__main__":
    # Quick manual smoke test — run `python input_handler.py`
    good = {
        "start_date": "2026-09-10",
        "end_date": "2026-09-20",
        "budget": 1500,
        "currency": "usd",
        "interests": ["food", "Nature", "adventure"],
    }
    print("Valid request ->", parse_trip_request(good))

    bad = {
        "start_date": "2026-09-20",
        "end_date": "2026-09-10",  # before start_date
        "budget": -50,
        "currency": "US",
        "interests": ["food", "skiing"],  # "skiing" isn't allowed
    }
    try:
        parse_trip_request(bad)
    except TripRequestError as exc:
        print("Invalid request errors ->")
        for e in exc.errors:
            print(" -", e)