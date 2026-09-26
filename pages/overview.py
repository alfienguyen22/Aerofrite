import streamlit as st

from src.app_state import (
    get_planning_state,
)


planning = get_planning_state()


st.title(
    "🏠 Network Overview"
)

st.write(
    """
    Optimize Aerofrite's weekly route network from
    Brussels by allocating limited Airbus A320neo
    fleet capacity across candidate European markets.
    """
)

st.info(
    (
        f"Current scenario: "
        f"{planning['fleet_size']} aircraft • "
        f"{planning['season'].title()} • "
        f"{planning['operational_buffer_percent']}% "
        f"operational reserve"
    )
)

st.caption(
    "Network Overview content will be moved here next."
)