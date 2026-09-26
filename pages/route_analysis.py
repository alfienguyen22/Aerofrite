import streamlit as st

from src.app_state import (
    get_planning_state,
)


planning = get_planning_state()


st.title(
    "🔎 Route Analysis"
)

st.write(
    """
    Inspect individual candidate routes and understand
    how commercial demand, frequency, capacity, and
    economics influence network selection.
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