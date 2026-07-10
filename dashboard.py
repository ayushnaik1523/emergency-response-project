"""Streamlit dashboard: submit reports and review agent decisions.

Run with: streamlit run dashboard.py
"""

import json
import streamlit as st
from pathlib import Path
from src.models import RawReport
from src.orchestrator import Orchestrator

st.set_page_config(page_title="Emergency Response Agent", layout="centered")

if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = Orchestrator()
if "results" not in st.session_state:
    st.session_state.results = []

orchestrator = st.session_state.orchestrator

st.title("🚨 Emergency Response Agent — Dashboard")
st.caption("Agentic AI pipeline: Intake → Triage → Resource → Comms, with human-in-the-loop review.")

with st.expander("Load a sample report"):
    sample_path = Path(__file__).parent / "data" / "sample_reports.json"
    samples = json.loads(sample_path.read_text())
    labels = [f"{s['id']}: {s['text'][:60]}..." for s in samples]
    choice = st.selectbox("Sample reports", options=range(len(samples)), format_func=lambda i: labels[i])
    if st.button("Use this sample"):
        st.session_state["prefill"] = samples[choice]

report_id = st.text_input("Report ID", value=st.session_state.get("prefill", {}).get("id", "R100"))
text = st.text_area("Report text", value=st.session_state.get("prefill", {}).get("text", ""))
col1, col2 = st.columns(2)
lat = col1.number_input("Latitude", value=float(st.session_state.get("prefill", {}).get("lat", 40.7128)))
lon = col2.number_input("Longitude", value=float(st.session_state.get("prefill", {}).get("lon", -74.0060)))

if st.button("Submit report", type="primary"):
    raw = RawReport(id=report_id, text=text, lat=lat, lon=lon)
    result = orchestrator.handle_report(raw)
    st.session_state.results.insert(0, result)

st.divider()
st.subheader("Incident results")

for result in st.session_state.results:
    with st.container(border=True):
        header = f"**{result.report_id}** — {result.triage.emergency_type.upper()} · Severity {result.triage.severity}/5"
        if result.requires_human_review:
            header += "  🔶 NEEDS HUMAN REVIEW"
        st.markdown(header)

        if result.duplicate_of:
            st.warning(f"Possible duplicate of incident {result.duplicate_of}")

        st.write(f"**Reasoning:** {result.triage.reasoning}")
        st.write(f"**Assigned unit:** {result.resource.unit_id or 'None available'} "
                  f"({result.resource.distance_km} km away)" if result.resource.unit_id else
                  "**Assigned unit:** None available")
        st.write(f"**Caller message:** {result.comms.caller_message}")
        st.write(f"**Responder alert:** {result.comms.responder_alert}")

        if result.requires_human_review:
            c1, c2 = st.columns(2)
            if c1.button("✅ Approve dispatch", key=f"approve_{result.report_id}"):
                st.success(f"Dispatch approved for {result.report_id}")
            if c2.button("❌ Reject / escalate", key=f"reject_{result.report_id}"):
                st.error(f"Dispatch rejected for {result.report_id} — escalate manually")
