"""
STUB VERSION — fake, hardcoded data so the agent loop can be built and tested
before the real backend (Person B's tools.py) is ready. Swap this file out
later; keep the function names and return shapes identical so agent.py
doesn't need to change.
"""

STUB_TRANSPORT = [
    {"origin": "Pune", "destination": "Mahabaleshwar", "mode": "cab", "cost": 2500, "duration_hrs": 3},
    {"origin": "Pune", "destination": "Mahabaleshwar", "mode": "bus", "cost": 400, "duration_hrs": 4},
    {"origin": "Mumbai", "destination": "Nagpur", "mode": "flight", "cost": 3200, "duration_hrs": 1.5},
    {"origin": "Mumbai", "destination": "Nagpur", "mode": "train", "cost": 900, "duration_hrs": 14},
]

STUB_HOTELS = [
    {"destination": "Mahabaleshwar", "name": "Hotel Grand View", "price_per_night": 2200, "rating": 4.1},
    {"destination": "Mahabaleshwar", "name": "Valley Inn", "price_per_night": 1400, "rating": 3.7},
    {"destination": "Nagpur", "name": "Orange City Suites", "price_per_night": 1800, "rating": 4.0},
]

STUB_ACTIVITIES = {
    "Mahabaleshwar": [
        {"name": "Venna Lake Boating", "tag": "nature", "cost": 200},
        {"name": "Mapro Garden", "tag": "food", "cost": 0},
        {"name": "Arthur's Seat Viewpoint", "tag": "nature", "cost": 0},
    ],
    "Nagpur": [
        {"name": "Deekshabhoomi", "tag": "culture", "cost": 0},
        {"name": "Zero Mile Stone", "tag": "culture", "cost": 0},
    ],
}


def search_transport(origin: str, destination: str, date: str) -> list:
    results = [r for r in STUB_TRANSPORT if r["origin"] == origin and r["destination"] == destination]
    return results if results else [{"error": f"No transport data for {origin} to {destination} in stub set"}]


def search_hotels(destination: str, nights: int, max_price_per_night: float = None) -> list:
    results = [h for h in STUB_HOTELS if h["destination"] == destination]
    if max_price_per_night is not None:
        results = [h for h in results if h["price_per_night"] <= max_price_per_night]
    return results if results else [{"error": f"No hotels found for {destination} within budget"}]


def search_activities(destination: str, interests: list) -> list:
    all_acts = STUB_ACTIVITIES.get(destination, [])
    matched = [a for a in all_acts if a["tag"] in interests]
    return matched if matched else all_acts


def calculate_budget(transport_cost: float, hotel_cost: float, activities_cost: float, total_budget: float) -> dict:
    spent = transport_cost + hotel_cost + activities_cost
    return {
        "total_spent": spent,
        "budget_remaining": total_budget - spent,
        "within_budget": spent <= total_budget,
    }


if __name__ == "__main__":
    print(search_transport("Pune", "Mahabaleshwar", "2026-09-10"))
    print(search_hotels("Mahabaleshwar", nights=2, max_price_per_night=2000))
    print(search_activities("Mahabaleshwar", ["nature", "food"]))
    print(calculate_budget(2500, 2800, 200, 10000))