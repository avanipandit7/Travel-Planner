import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";

// Origins the stub data supports right now. When your partner's real transport
// data is ready, add the new cities here (names must match the data exactly).
const ORIGINS = ["Pune", "Delhi", "Bangalore"];

const INTERESTS = [
  { value: "food", label: "Food" },
  { value: "culture", label: "Culture" },
  { value: "adventure", label: "Adventure" },
  { value: "nature", label: "Nature" },
  { value: "nightlife", label: "Nightlife" },
  { value: "shopping", label: "Shopping" },
];

const MAX_NIGHTS = 10;

// Today's date as YYYY-MM-DD in the user's own timezone (used as the minimum for the date pickers)
function todayString() {
  const d = new Date();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${d.getFullYear()}-${month}-${day}`;
}

// Same checks the server does, so the user gets instant feedback without waiting
function validateForm({ origin, startDate, endDate, budget, interests }) {
  if (!origin) return "Please choose an origin city.";
  if (!startDate || !endDate) return "Please pick both a start date and an end date.";
  if (startDate < todayString()) return "The start date can't be in the past.";
  const nights = (new Date(endDate) - new Date(startDate)) / 86400000;
  if (nights < 1) return "The end date must be after the start date.";
  if (nights > MAX_NIGHTS) return `Trips can be at most ${MAX_NIGHTS} nights.`;
  if (!budget || Number(budget) <= 0) return "Please enter a budget greater than zero.";
  if (interests.length === 0) return "Pick at least one interest.";
  return null;
}

export default function App() {
  // ---- form state ----
  const [origin, setOrigin] = useState(ORIGINS[0]);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [budget, setBudget] = useState("8000");
  const [interests, setInterests] = useState(["nature", "food"]);

  // ---- request state ----
  const [loading, setLoading] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [tab, setTab] = useState("trip"); // "trip" or "trace"

  // Counts seconds while a request is running, so the user can see it hasn't frozen
  useEffect(() => {
    if (!loading) return;
    setElapsed(0);
    const id = setInterval(() => setElapsed((s) => s + 1), 1000);
    return () => clearInterval(id);
  }, [loading]);

  function toggleInterest(value) {
    setInterests((current) =>
      current.includes(value) ? current.filter((i) => i !== value) : [...current, value]
    );
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (loading) return;

    const problem = validateForm({ origin, startDate, endDate, budget, interests });
    if (problem) {
      setError(problem);
      return;
    }

    setError("");
    setResult(null);
    setTab("trip");
    setLoading(true);

    try {
      const response = await fetch("/api/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          origin,
          start_date: startDate,
          end_date: endDate,
          budget: Number(budget),
          interests,
        }),
      });

      // If the server isn't running, the response won't be valid JSON
      let data = null;
      try {
        data = await response.json();
      } catch {
        data = null;
      }

      if (!response.ok || !data) {
        setError(
          data?.error ||
            "Could not reach the server. Is `python server.py` running in the backend folder?"
        );
        return;
      }
      setResult(data);
    } catch {
      setError("Network error. Is `python server.py` running in the backend folder?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <header className="header">
        <h1>TripAgent</h1>
        <p>An AI agent that plans your Mumbai trip within your budget.</p>
      </header>

      <form className="card form" onSubmit={handleSubmit} noValidate>
        <div className="row">
          <label>
            Travelling from
            <select value={origin} onChange={(e) => setOrigin(e.target.value)}>
              {ORIGINS.map((city) => (
                <option key={city} value={city}>
                  {city}
                </option>
              ))}
            </select>
          </label>

          <label>
            Budget (INR)
            <input
              type="number"
              min="0"
              step="100"
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
            />
          </label>
        </div>

        <div className="row">
          <label>
            Start date
            <input
              type="date"
              min={todayString()}
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </label>

          <label>
            End date
            <input
              type="date"
              min={startDate || todayString()}
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
          </label>
        </div>

        <div className="field">
          <span className="field-label">Interests</span>
          <div className="chips">
            {INTERESTS.map(({ value, label }) => (
              <button
                type="button"
                key={value}
                className={interests.includes(value) ? "chip chip-on" : "chip"}
                onClick={() => toggleInterest(value)}
                aria-pressed={interests.includes(value)}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        <button type="submit" className="primary" disabled={loading}>
          {loading ? "Planning…" : "Plan my trip"}
        </button>
      </form>

      {loading && (
        <div className="card status" role="status">
          <div className="spinner" aria-hidden="true" />
          <div>
            <strong>The agent is planning your trip… ({elapsed}s)</strong>
            <p>
              It is searching transport, hotels and activities, then checking your budget. This
              usually takes 15–60 seconds.
            </p>
          </div>
        </div>
      )}

      {error && (
        <div className="card error" role="alert">
          {error}
        </div>
      )}

      {result && (
        <div className="card result">
          <p className="request-text">{result.request_text}</p>

          {!result.finished && (
            <p className="warning">
              The agent stopped before finishing (it hit its step limit). Check the Agent Trace to
              see what it did.
            </p>
          )}

          <div className="tabs" role="tablist">
            <button
              role="tab"
              aria-selected={tab === "trip"}
              className={tab === "trip" ? "tab tab-on" : "tab"}
              onClick={() => setTab("trip")}
            >
              Trip View
            </button>
            <button
              role="tab"
              aria-selected={tab === "trace"}
              className={tab === "trace" ? "tab tab-on" : "tab"}
              onClick={() => setTab("trace")}
            >
              Agent Trace ({result.trace.length} tool calls)
            </button>
          </div>

          {tab === "trip" ? (
            <div className="markdown">
              <ReactMarkdown>{result.itinerary}</ReactMarkdown>
            </div>
          ) : (
            <div className="trace">
              {result.trace.length === 0 && <p>The agent did not call any tools.</p>}
              {result.trace.map((step) => (
                <details key={step.step} className="trace-step">
                  <summary>
                    <span className="step-num">Step {step.step}</span>
                    <code>{step.tool}</code>
                  </summary>
                  <p className="trace-label">Arguments the agent sent</p>
                  <pre>{JSON.stringify(step.args, null, 2)}</pre>
                  <p className="trace-label">What the tool returned</p>
                  <pre>{JSON.stringify(step.result, null, 2)}</pre>
                </details>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
