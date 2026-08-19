from google.genai import types

TRANSPORT_DECL = types.FunctionDeclaration(
    name="search_transport",
    description=(
        "Find transport options (flight, train, bus, or cab) between an origin "
        "and a destination in Maharashtra on a given date. Returns a list of "
        "options with mode, cost, and duration."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "origin": {"type": "string", "description": "Starting city, e.g. 'Pune'"},
            "destination": {"type": "string", "description": "Destination city, e.g. 'Mahabaleshwar'"},
            "date": {"type": "string", "description": "Travel date, format YYYY-MM-DD"},
        },
        "required": ["origin", "destination", "date"],
    },
)

HOTEL_DECL = types.FunctionDeclaration(
    name="search_hotels",
    description=(
        "Find hotels in a given destination, optionally filtered by a maximum "
        "price per night. Returns a list of hotels with name, price, and rating."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "destination": {"type": "string", "description": "City to search hotels in"},
            "nights": {"type": "integer", "description": "Number of nights the traveler will stay"},
            "max_price_per_night": {"type": "number", "description": "Optional upper price limit per night"},
        },
        "required": ["destination", "nights"],
    },
)

ACTIVITY_DECL = types.FunctionDeclaration(
    name="search_activities",
    description=(
        "Find activities/attractions in a destination that match the traveler's "
        "interests (e.g. food, nature, culture, adventure, nightlife, shopping)."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "destination": {"type": "string"},
            "interests": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of interest tags to filter by, e.g. ['nature', 'food']",
            },
        },
        "required": ["destination", "interests"],
    },
)

BUDGET_DECL = types.FunctionDeclaration(
    name="calculate_budget",
    description=(
        "Check whether the sum of transport, hotel, and activity costs fits "
        "within the traveler's total budget. Call this AFTER gathering transport, "
        "hotel, and activity costs — it should be the last tool called."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "transport_cost": {"type": "number"},
            "hotel_cost": {"type": "number", "description": "Total hotel cost = price_per_night * nights"},
            "activities_cost": {"type": "number", "description": "Sum of all planned activity costs"},
            "total_budget": {"type": "number", "description": "The traveler's stated total budget"},
        },
        "required": ["transport_cost", "hotel_cost", "activities_cost", "total_budget"],
    },
)

TRIP_TOOL = types.Tool(
    function_declarations=[TRANSPORT_DECL, HOTEL_DECL, ACTIVITY_DECL, BUDGET_DECL]
)