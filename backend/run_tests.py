"""
Day 3: run several different requests through the agent and watch the trace.
This is the real "mastering the agent" step — reading what it actually does,
not just confirming it runs once.
"""
from agent import plan_trip

TEST_REQUESTS = [
    # 1. Normal case — should work cleanly, both destinations exist in stub data
    "Plan a trip from Pune to Mahabaleshwar, 2026-09-10 to 2026-09-12 (2 nights), "
    "budget 8000 INR, interested in nature and food.",

    # 2. Different route + different interest — tests whether it actually
    #    filters activities by interest, not just returning everything
    "Plan a trip from Mumbai to Nagpur, 2026-10-01 to 2026-10-03 (2 nights), "
    "budget 6000 INR, interested in culture.",

    # 3. Deliberately tight budget — does it pick the cheaper hotel (Valley Inn,
    #    not Hotel Grand View) and/or trim activities to fit? Or does it just
    #    report "over budget" and give up?
    "Plan a trip from Pune to Mahabaleshwar, 2026-09-10 to 2026-09-11 (1 night), "
    "budget 2000 INR, interested in nature.",

    # 4. A destination NOT in the stub data at all — tests how gracefully it
    #    handles a tool returning an error/empty result instead of crashing
    #    or hallucinating fake data
    "Plan a trip from Pune to Kolhapur, 2026-09-15 to 2026-09-17 (2 nights), "
    "budget 5000 INR, interested in food and shopping.",
]

if __name__ == "__main__":
    for i, request in enumerate(TEST_REQUESTS, start=1):
        print("=" * 70)
        print(f"TEST {i}: {request}")
        print("=" * 70)
        result = plan_trip(request)
        print("\n--- FINAL ITINERARY ---")
        print(result)
        print("\n")