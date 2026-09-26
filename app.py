import streamlit as st


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Aerofrite Network Planner",
    page_icon="✈️",
    layout="wide",
)


# --------------------------------------------------
# Shared planning controls
# --------------------------------------------------

st.sidebar.title("✈️ Aerofrite")

st.sidebar.caption(
    "Airline Network Planning & Optimization"
)

st.sidebar.divider()

st.sidebar.header(
    "Planning Controls"
)


fleet_size = st.sidebar.slider(
    "Fleet size",
    min_value=0,
    max_value=10,
    value=5,
    step=1,
    key="fleet_size",
    help=(
        "Number of Airbus A320neo aircraft "
        "available to Aerofrite."
    ),
)


season = st.sidebar.selectbox(
    "Planning season",
    options=[
        "winter",
        "shoulder",
        "summer",
    ],
    index=1,
    format_func=lambda value: value.title(),
    key="season",
    help=(
        "Season changes modeled market demand "
        "by market type."
    ),
)


operational_buffer_percent = (
    st.sidebar.slider(
        "Operational reserve",
        min_value=0,
        max_value=25,
        value=10,
        step=1,
        format="%d%%",
        key="operational_buffer_percent",
        help=(
            "Share of theoretical aircraft capacity "
            "reserved for maintenance, disruption "
            "recovery, and operational flexibility."
        ),
    )
)


st.sidebar.caption(
    """
    Route decisions are discrete, so nearby reserve
    levels may produce the same optimized network until
    a capacity threshold is crossed.
    """
)


# --------------------------------------------------
# Navigation
# --------------------------------------------------

pages = {
    "Network Planning": [
        st.Page(
            "pages/overview.py",
            title="Network Overview",
            icon="🏠",
            default=True,
        ),

        st.Page(
            "pages/route_analysis.py",
            title="Route Analysis",
            icon="🔎",
        ),

        st.Page(
            "pages/scenario_analysis.py",
            title="Scenario Analysis",
            icon="📊",
        ),

        st.Page(
            "pages/demand_model.py",
            title="Demand & Market Model",
            icon="📈",
        ),
    ],

    "Project": [
        st.Page(
            "pages/case_study.py",
            title="Case Study",
            icon="📋",
        ),

        st.Page(
            "pages/methodology.py",
            title="Methodology",
            icon="ℹ️",
        ),
    ],
}


navigation = st.navigation(
    pages
)

navigation.run()