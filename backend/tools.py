"""
STUB VERSION — fake, hardcoded data so the agent loop can be tested before
Person B's real Mumbai dataset is ready. Destination is always Mumbai now;
origin varies. Keep function names/return shapes identical when swapping
in real data later — agent.py shouldn't need to change.
"""

STUB_TRANSPORT = [
    {"origin": "Pune", "destination": "Mumbai", "mode": "train", "cost": 350, "duration_hrs": 3.5},
    {"origin": "Pune", "destination": "Mumbai", "mode": "bus", "cost": 450, "duration_hrs": 4},
    {"origin": "Delhi", "destination": "Mumbai", "mode": "flight", "cost": 4200, "duration_hrs": 2.2},
    {"origin": "Delhi", "destination": "Mumbai", "mode": "train", "cost": 1800, "duration_hrs": 16},
    {"origin": "Bangalore", "destination": "Mumbai", "mode": "flight", "cost": 3500, "duration_hrs": 1.8},
]

STUB_HOTELS = [
    {"destination": "Mumbai", "area": "Colaba", "name": "Sea Breeze Residency", "price_per_night": 3200, "rating": 4.2},
    {"destination": "Mumbai", "area": "Bandra", "name": "Bandra Boutique Stay", "price_per_night": 2800, "rating": 4.0},
    {"destination": "Mumbai", "area": "Andheri", "name": "Andheri Business Hotel", "price_per_night": 1800, "rating": 3.8},
    {"destination": "Mumbai", "area": "Juhu", "name": "Juhu Beach View Inn", "price_per_night": 2400, "rating": 4.1},
    {"destination": "Mumbai", "area": "Powai", "name": "Powai Lake Suites", "price_per_night": 2000, "rating": 3.9},
]

STUB_ACTIVITIES = {
    "Mumbai": [
        {"name": "Gateway of India", "area": "Colaba", "tag": "culture", "cost": 0},
        {"name": "Bandra-Worli Sea Link viewpoint", "area": "Bandra", "tag": "nature", "cost": 0},
        {"name": "Mohammed Ali Road food walk", "area": "South Mumbai", "tag": "food", "cost": 500},
        {"name": "Juhu Beach", "area": "Juhu", "tag": "nature", "cost": 0},
        {"name": "Colaba Causeway shopping", "area": "Colaba", "tag": "shopping", "cost": 0},
        {"name": "Bandra nightlife strip", "area": "Bandra", "tag": "nightlife", "cost": 800},
        {"name": "Elephanta Caves", "area": "Mumbai Harbour", "tag": "culture", "cost": 600},
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
    print(search_transport("Pune", "Mumbai", "2026-09-10"))
    print(search_hotels("Mumbai", nights=2, max_price_per_night=2500))
    print(search_activities("Mumbai", ["nature", "food"]))
    print(calculate_budget(350, 4800, 500, 10000))