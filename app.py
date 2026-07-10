"""FastAPI backend exposing the emergency response pipeline.

Run with: uvicorn app:app --reload
Then POST to /report, e.g.:

curl -X POST http://localhost:8000/report \
  -H "Content-Type: application/json" \
  -d '{"id": "R100", "text": "Fire on Main St, people trapped", "lat": 40.71, "lon": -74.00}'
"""

from fastapi import FastAPI
from src.models import RawReport, IncidentResult
from src.orchestrator import Orchestrator

app = FastAPI(title="Emergency Response Agent API")
orchestrator = Orchestrator()


@app.get("/")
def root():
    return {"status": "ok", "message": "Emergency Response Agent API is running."}


@app.post("/report", response_model=IncidentResult)
def submit_report(raw: RawReport) -> IncidentResult:
    return orchestrator.handle_report(raw)


@app.get("/incidents")
def list_incidents():
    rows = orchestrator.memory.all_incidents()
    columns = ["report_id", "text", "lat", "lon", "emergency_type", "severity", "timestamp"]
    return [dict(zip(columns, row)) for row in rows]
