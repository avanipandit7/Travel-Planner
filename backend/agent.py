import os
import json
from dotenv import load_dotenv
import anthropic

from tool_schemas import ALL_TOOLS
from tools import search_transport, search_hotels, search_activities, calculate_budget

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a travel planning agent for trips within Maharashtra, India.

Given a trip request (origin, destination, start date, end date, budget, interests),
your job is to build a complete day-wise itinerary that fits within the stated budget.

You have four tools available:
- search_transport: find transport between origin and destination
- search_hotels: find hotels at the destination
- search_activities: find activities matching the traveler's interests
- calculate_budget: check total cost against the budget (call this LAST, after you have transport, hotel, and activity costs)

Order: 
1. Search transport first.
2. Search hotels, filtered to a reasonable price given the budget.
3. Search activities matching the traveler's interests.
4. Call calculate_budget once you have all three costs.

If calculate_budget shows the plan is over budget, try a cheaper hotel or fewer paid
activities and recalculate — don't just report it's over budget and stop.

Once you have transport, a hotel, activities for each day, and a budget check that
passes, STOP calling tools and respond with a final plain-text summary of the itinerary:
transport choice, hotel choice, a day-by-day list of activities, and total cost vs budget.
"""

TOOL_FUNCTIONS = {
    "search_transport": search_transport,
    "search_hotels": search_hotels,
    "search_activities": search_activities,
    "calculate_budget": calculate_budget,
}

MAX_ITERATIONS = 8


def call_tool(name: str, tool_input: dict):
    fn = TOOL_FUNCTIONS.get(name)
    if fn is None:
        return {"error": f"Unknown tool: {name}"}
    try:
        return fn(**tool_input)
    except Exception as e:
        return {"error": f"Tool {name} failed: {str(e)}"}


def plan_trip(trip_request_text: str, verbose: bool = True):
    messages = [{"role": "user", "content": trip_request_text}]

    for iteration in range(MAX_ITERATIONS):
        response = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            tools=ALL_TOOLS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            final_text = "".join(b.text for b in response.content if b.type == "text")
            return final_text

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                if verbose:
                    print(f"  [iteration {iteration+1}] calling {block.name}({block.input})")
                result = call_tool(block.name, block.input)
                if verbose:
                    print(f"    -> {result}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
                })
        messages.append({"role": "user", "content": tool_results})

    return "Agent hit the iteration limit without finishing. Check the trace above."


if __name__ == "__main__":
    request = (
        "Plan a trip from Pune to Mahabaleshwar, 2026-09-10 to 2026-09-12 "
        "(2 nights), budget 8000 INR, interested in nature and food."
    )
    print(f"Request: {request}\n")
    result = plan_trip(request)
    print("\n--- FINAL ITINERARY ---")
    print(result)