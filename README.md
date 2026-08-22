# Waypoint — AI Travel Planning Chatbot

A full-stack travel planning app centered on a conversational assistant that
turns a budget and a few preferences into a complete, budget-aware trip plan
— without ever redirecting you to a payment page.

## What it does
- Collects trip budget, currency, pace, climate, and group-type through a
  guided chatbot flow
- Matches you to a destination based on your answers
- Generates a day-by-day itinerary covering food, activities, and nearby
  healthcare options
- Converts currency live via a real exchange-rate API
- Includes an agentic planning layer (Gemini + tool-calling) that searches
  transport, hotels, and activities, then checks and adjusts the plan
  against your stated budget automatically

## Tech stack
- **Frontend:** React (Vite)
- **Backend:** Python (Flask)
- **Database:** SQL
- **AI:** Google Gemini API with function calling for agentic itinerary planning

## Status
Actively in development — chatbot flow and currency conversion are working
end-to-end; the agentic planning layer currently runs on stub data ahead of
live transport/hotel/activity APIs. Group chat mode (multi-user trip
planning) is planned next.
