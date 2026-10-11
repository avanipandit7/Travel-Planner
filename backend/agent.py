import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

from tool_schemas import TRIP_TOOL
from tools import search_transport, search_hotels, search_activities, calculate_budget

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-3.5-Flash lite"  # check https://ai.dev/rate-limit for current free-tier limits

SYSTEM_PROMPT = """You are a travel planning agent for trips to Mumbai, India.
"""

TOOL_FUNCTIONS = {
    "search_transport": search_transport,
    "search_hotels": search_hotels,
    "search_activities": search_activities,
    "calculate_budget": calculate_budget,
}

MAX_ITERATIONS = 8

CONFIG = types.GenerateContentConfig(
    system_instruction=SYSTEM_PROMPT,
    tools=[TRIP_TOOL],
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
)


def call_tool(name: str, tool_input: dict):
    fn = TOOL_FUNCTIONS.get(name)
    if fn is None:
        return {"error": f"Unknown tool: {name}"}
    try:
        return fn(**tool_input)
    except Exception as e:
        return {"error": f"Tool {name} failed: {str(e)}"}


def _to_plain(obj):
    """Make tool args/results safe to send as JSON (anything odd becomes a string)."""
    return json.loads(json.dumps(obj, default=str))


def run_agent(trip_request_text: str, verbose: bool = True) -> dict:
    """
    Runs the full agent loop and returns EVERYTHING, not just the final text:
      {
        "itinerary": the final text the agent wrote,
        "trace":     a list of every tool call it made (name, args, result),
        "finished":  False if it hit MAX_ITERATIONS without finishing
      }
    The web server uses this so the frontend can show both the itinerary
    and the "Agent Trace View".
    """
    contents = [types.Content(role="user", parts=[types.Part.from_text(text=trip_request_text)])]
    trace = []

    for iteration in range(MAX_ITERATIONS):
        response = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=CONFIG,
        )
        contents.append(response.candidates[0].content)

        function_calls = response.function_calls
        if not function_calls:
            return {
                "itinerary": response.text or "(The agent finished but returned no text.)",
                "trace": trace,
                "finished": True,
            }

        function_response_parts = []
        for fc in function_calls:
            args = dict(fc.args) if fc.args else {}
            if verbose:
                print(f"  [iteration {iteration+1}] calling {fc.name}({args})")
            result = call_tool(fc.name, args)
            if verbose:
                print(f"    -> {result}")
            trace.append({
                "step": len(trace) + 1,
                "tool": fc.name,
                "args": _to_plain(args),
                "result": _to_plain(result),
            })
            function_response_parts.append(
                types.Part.from_function_response(name=fc.name, response={"result": result})
            )

        contents.append(types.Content(role="user", parts=function_response_parts))

    return {
        "itinerary": "The agent hit the iteration limit without finishing. See the Agent Trace for what it did.",
        "trace": trace,
        "finished": False,
    }


def plan_trip(trip_request_text: str, verbose: bool = True) -> str:
    """Same as before: returns just the itinerary text (run_tests.py still uses this)."""
    return run_agent(trip_request_text, verbose)["itinerary"]


if __name__ == "__main__":
    request = (
        "Plan a trip from Pune to Mumbai, 2026-09-10 to 2026-09-12 "
        "(2 nights), budget 8000 INR, interested in nature and food."
    )
    print(f"Request: {request}\n")
    result = plan_trip(request)
    print("\n--- FINAL ITINERARY ---")
    print(result)