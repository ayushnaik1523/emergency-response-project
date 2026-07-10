# Emergency Response Agent — Starter Project

A multi-agent "agentic AI" system that ingests emergency reports, triages them,
assigns the nearest available responder unit, drafts communications, and
routes high-severity/ambiguous cases to a human for approval before dispatch.

See `docs/emergency_response_agent_project.md` for the full project plan,
architecture diagram, milestones, and evaluation plan this code implements.

## Project Structure

```
emergency_response_agent/
├── README.md
├── requirements.txt
├── .env.example
├── docs/
│   └── emergency_response_agent_project.md   # full project plan
├── data/
│   ├── units.json            # mock responder units (ambulances, fire, police)
│   └── sample_reports.json   # sample emergency reports for testing/demo
├── src/
│   ├── __init__.py
│   ├── models.py             # Pydantic schemas shared across agents
│   ├── llm_client.py         # thin wrapper around the LLM API (optional)
│   ├── intake_agent.py       # parses raw report text into structured data
│   ├── triage_agent.py       # classifies type + severity
│   ├── resource_agent.py     # finds nearest available unit
│   ├── comms_agent.py        # drafts caller reply + responder alert
│   ├── memory.py             # simple SQLite log + duplicate-incident check
│   └── orchestrator.py       # coordinates the agents (the "agentic" core)
├── app.py                    # FastAPI backend exposing /report endpoint
├── dashboard.py               # Streamlit human-in-the-loop review dashboard
└── tests/
    └── test_pipeline.py       # end-to-end pipeline test on sample reports
```

## Quickstart

```bash
# 1. Create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Add an LLM API key for smarter triage/comms
cp .env.example .env
# edit .env and add ANTHROPIC_API_KEY=sk-...
# The system works WITHOUT a key too — it falls back to rule-based
# keyword triage so you can demo it immediately.

# 4. Run the end-to-end pipeline on sample data (no server needed)
python -m tests.test_pipeline

# 5. Run the API
uvicorn app:app --reload
# POST to http://localhost:8000/report  with {"text": "..."}

# 6. Run the human-in-the-loop dashboard
streamlit run dashboard.py
```

## How the "agentic" part works

`src/orchestrator.py` is the core: it does NOT follow a fixed script. It runs
a loop that:
1. Calls the **Intake Agent** to structure the raw report.
2. Calls the **Triage Agent** to classify severity/type.
3. Checks **Memory** for duplicate/nearby recent incidents.
4. Decides (based on severity) whether to auto-continue or flag for **human
   review** — this branching decision is the "planning" step.
5. Calls the **Resource Agent** to find the nearest available unit.
6. Calls the **Communication Agent** to draft messages.
7. Logs everything to memory for future duplicate-detection and analytics.

Each agent is a plain Python class with a single `run()` method, so you can
swap in LangGraph/CrewAI later without changing the interfaces — the project
plan doc explains how to extend this into a full LangGraph state machine as
a stretch goal.

## Notes for your report

- The rule-based fallback (`src/triage_agent.py`) is intentionally simple and
  documented — use it as your baseline, then show improvement when you plug
  in an LLM (`llm_client.py`) or a trained classifier. That before/after
  comparison is good evaluation material for your writeup.
- `data/units.json` and `data/sample_reports.json` are mock data — replace
  with real/synthetic data as described in the project plan.
