import streamlit as st


def get_planning_state():
    """
    Return the planning assumptions selected
    in the global Streamlit sidebar.
    """

    fleet_size = st.session_state.get(
        "fleet_size",
        5,
    )

    season = st.session_state.get(
        "season",
        "shoulder",
    )

    operational_buffer_percent = (
        st.session_state.get(
            "operational_buffer_percent",
            10,
        )
    )

    operational_buffer = (
        operational_buffer_percent
        / 100
    )

    return {
        "fleet_size":
            fleet_size,

        "season":
            season,

        "operational_buffer_percent":
            operational_buffer_percent,

        "operational_buffer":
            operational_buffer,
    }

