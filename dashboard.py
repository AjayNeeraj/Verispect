import streamlit as st
import pandas as pd
import aiosqlite
import asyncio
import plotly.express as px

DB_PATH = "verispect.db"

async def get_logs():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM logs ORDER BY created_at DESC") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

def load_data():
    return asyncio.run(get_logs())

st.set_page_config(page_title="Verispect", layout="wide")
st.title("Verispect — AI Model Monitor")
st.caption("Real-time drift detection across your LLM traffic")

df = pd.DataFrame(load_data())

if df.empty:
    st.warning("No data yet. Make some API calls through Verispect.")
    st.stop()

# --- Metrics ---
total_calls = len(df[df["is_canary"] == 0])
total_probes = len(df[df["is_canary"] == 1])
total_flagged = len(df[df["flagged"] == 1])
avg_drift = df[df["is_canary"] == 1]["drift_score"].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total API Calls", total_calls)
col2.metric("Probes Fired", total_probes)
col3.metric("Drift Events", total_flagged)
col4.metric("Avg Drift Score", f"{avg_drift:.4f}" if not pd.isna(avg_drift) else "N/A")

st.divider()

# --- Drift timeline ---
canary_df = df[df["is_canary"] == 1].copy()

if not canary_df.empty:
    st.subheader("Drift score over time")
    canary_df["created_at"] = pd.to_datetime(canary_df["created_at"])
    fig = px.scatter(
        canary_df,
        x="created_at",
        y="drift_score",
        color="flagged",
        color_discrete_map={0: "green", 1: "red"},
        hover_data=["probe_id", "drift_score"],
        labels={"drift_score": "Drift Score", "created_at": "Time", "flagged": "Flagged"}
    )
    fig.add_hline(y=0.18, line_dash="dash", line_color="red", annotation_text="Drift threshold")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- Flagged events ---
st.subheader("Drift events")
flagged_df = df[df["flagged"] == 1][["created_at", "probe_id", "drift_score", "model", "response"]]
if flagged_df.empty:
    st.success("No drift events detected.")
else:
    st.dataframe(flagged_df, use_container_width=True)

st.divider()

# --- Full log ---
st.subheader("Full call log")
display_df = df[["created_at", "model", "prompt", "response", "prompt_tokens", "completion_tokens", "latency_ms", "is_canary", "drift_score", "flagged"]].copy()
st.dataframe(display_df, use_container_width=True)

# --- Refresh button ---
if st.button("Refresh data"):
    st.rerun()
