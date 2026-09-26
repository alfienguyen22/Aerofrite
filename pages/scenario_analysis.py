import streamlit as st

from src.app_state import (
    get_planning_state,
)


planning = get_planning_state()


st.title(
    "📊 Scenario Analysis"
)

st.write(
    """
    Compare alternative fleet, season, and operational
    resilience scenarios.
    """
)

st.info(
    (
        f"Current scenario: "
        f"{planning['fleet_size']} aircraft • "
        f"{planning['season'].title()} • "
        f"{planning['operational_buffer_percent']}% "
        f"reserve"
    )
)