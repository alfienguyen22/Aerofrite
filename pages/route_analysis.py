import streamlit as st

from src.app_state import (
    get_planning_state,
)
from src.app_services import (
    build_route_details,
    get_closed_route_analysis,
    get_optimized_network,
    get_route_frequency_analysis,
)


# --------------------------------------------------
# Planning state
# --------------------------------------------------

planning = get_planning_state()

fleet_size = planning[
    "fleet_size"
]

season = planning[
    "season"
]

operational_buffer = planning[
    "operational_buffer"
]

operational_buffer_percent = planning[
    "operational_buffer_percent"
]


# --------------------------------------------------
# Current optimized network
# --------------------------------------------------

result = get_optimized_network(
    fleet_size=fleet_size,
    season=season,
    operational_buffer=(
        operational_buffer
    ),
)

all_route_details = (
    build_route_details(
        result["routes"],
        active_only=False,
    )
)


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title(
    "🔎 Route Analysis"
)

st.write(
    """
    Inspect individual candidate routes and understand
    how demand, frequency, capacity, and economics
    influence Aerofrite's network decisions.
    """
)

st.caption(
    (
        f"Current planning scenario: "
        f"{fleet_size} aircraft • "
        f"{season.title()} • "
        f"{operational_buffer_percent}% "
        f"operational reserve"
    )
)


# --------------------------------------------------
# Route selector
# --------------------------------------------------

route_options = (
    all_route_details[
        "route_id"
    ]
    .sort_values()
    .tolist()
)

selected_route_id = st.selectbox(
    "Select a candidate route",
    options=route_options,
    key="route_inspector_route",
)

selected_route = (
    all_route_details[
        all_route_details[
            "route_id"
        ]
        == selected_route_id
    ]
    .iloc[0]
)


# --------------------------------------------------
# Route heading
# --------------------------------------------------

st.markdown(
    (
        f"## "
        f"{selected_route['route_id']} — "
        f"{selected_route['city']}"
    )
)

st.caption(
    (
        f"{selected_route['airport_name']} • "
        f"{selected_route['distance_km']:,.0f} km "
        f"from Brussels"
    )
)


if selected_route[
    "frequency"
] > 0:

    st.success(
        "Selected in the current optimized network"
    )

else:

    st.warning(
        "Not selected in the current optimized network"
    )


# --------------------------------------------------
# Current network decision
# --------------------------------------------------

st.markdown(
    "**Current Network Decision**"
)

decision_col1, decision_col2, (
    decision_col3
) = st.columns(3)

decision_col1.metric(
    "Weekly Frequency",
    (
        f"{int(selected_route['frequency'])}x"
    ),
)

decision_col2.metric(
    "Passengers",
    (
        f"{int(selected_route['passengers']):,}"
    ),
)

decision_col3.metric(
    "Load Factor",
    (
        f"{selected_route['load_factor']:.1%}"
    ),
)


decision_col4, decision_col5, (
    decision_col6
) = st.columns(3)

decision_col4.metric(
    "Weekly Contribution",
    (
        f"€"
        f"{selected_route['contribution']:,.0f}"
    ),
)

decision_col5.metric(
    "Contribution / Aircraft Hour",
    (
        f"€"
        f"{selected_route['contribution_per_aircraft_hour']:,.0f}"
    ),
)

decision_col6.metric(
    "Aircraft Hours",
    (
        f"{selected_route['aircraft_hours']:.1f}"
    ),
)


# --------------------------------------------------
# Commercial demand chain
# --------------------------------------------------

st.subheader(
    "Commercial Demand Chain"
)

context_col1, context_col2 = (
    st.columns(2)
)

context_col1.metric(
    "Planning Season",
    selected_route[
        "season"
    ].title(),
)

context_col2.metric(
    "Competition Level",
    selected_route[
        "competition_level"
    ].title(),
)


demand_col1, demand_col2, demand_col3 = (
    st.columns(3)
)

demand_col1.metric(
    "Base Weekly Demand",
    (
        f"{int(selected_route['weekly_demand']):,}"
    ),
)

demand_col2.metric(
    "Seasonal Factor",
    (
        f"{selected_route['seasonality_multiplier']:.0%}"
    ),
)

demand_col3.metric(
    "Competition Factor",
    (
        f"{selected_route['competition_multiplier']:.0%}"
    ),
)


adjusted_col1, adjusted_col2, (
    adjusted_col3
) = st.columns(3)

adjusted_col1.metric(
    "Adjusted Market Demand",
    (
        f"{int(selected_route['adjusted_market_demand']):,}"
    ),
)

adjusted_col2.metric(
    "Frequency Capture",
    (
        f"{selected_route['demand_multiplier']:.0%}"
    ),
)

adjusted_col3.metric(
    "Effective Demand",
    (
        f"{int(selected_route['effective_demand']):,}"
    ),
)


st.caption(
    """
    Base demand is adjusted for seasonality and
    competition before Aerofrite's frequency-response
    assumption is applied. Passengers carried are then
    limited by available seat capacity.
    """
)


# --------------------------------------------------
# Frequency option analysis
# --------------------------------------------------

st.subheader(
    "Frequency Option Analysis"
)

st.write(
    """
    Compare the standalone economics of each frequency
    available for this route. The network optimizer may
    choose a lower frequency — or close the route —
    because aircraft hours have alternative uses elsewhere
    in the network.
    """
)

frequency_analysis = (
    get_route_frequency_analysis(
        route_id=selected_route_id,
        season=season,
    )
)


frequency_display = (
    frequency_analysis[
        [
            "frequency",
            "effective_demand",
            "passengers",
            "load_factor",
            "contribution",
            "contribution_per_aircraft_hour",
            "aircraft_hours",
        ]
    ]
    .copy()
)


frequency_display[
    "Selected"
] = (
    frequency_display[
        "frequency"
    ]
    == int(
        selected_route[
            "frequency"
        ]
    )
)


frequency_display = (
    frequency_display.rename(
        columns={
            "frequency":
                "Weekly Frequency",

            "effective_demand":
                "Effective Demand",

            "passengers":
                "Passengers",

            "load_factor":
                "Load Factor",

            "contribution":
                "Contribution (€)",

            "contribution_per_aircraft_hour":
                "Contribution / Hour (€)",

            "aircraft_hours":
                "Aircraft Hours",
        }
    )
)


frequency_display[
    "Load Factor"
] = (
    frequency_display[
        "Load Factor"
    ]
    * 100
)


st.dataframe(
    frequency_display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Weekly Frequency":
            st.column_config.NumberColumn(
                format="%d",
            ),

        "Effective Demand":
            st.column_config.NumberColumn(
                format="%d",
            ),

        "Passengers":
            st.column_config.NumberColumn(
                format="%d",
            ),

        "Load Factor":
            st.column_config.NumberColumn(
                format="%.1f%%",
            ),

        "Contribution (€)":
            st.column_config.NumberColumn(
                format="localized",
            ),

        "Contribution / Hour (€)":
            st.column_config.NumberColumn(
                format="localized",
            ),

        "Aircraft Hours":
            st.column_config.NumberColumn(
                format="%.1f",
            ),

        "Selected":
            st.column_config.CheckboxColumn(
                "Selected",
            ),
    },
)


st.caption(
    """
    Frequency-option values evaluate this route in
    isolation. The final network decision also reflects
    fleet capacity and the opportunity cost of assigning
    aircraft hours to this route instead of another.
    """
)


# --------------------------------------------------
# Closed route analysis
# --------------------------------------------------

st.subheader(
    "Closed Route Analysis"
)

st.write(
    """
    Candidate routes may remain closed even when they
    have positive standalone contribution because scarce
    aircraft capacity can create greater contribution
    elsewhere in the network.
    """
)

closed_route_analysis = (
    get_closed_route_analysis(
        fleet_size=fleet_size,
        season=season,
        operational_buffer=(
            operational_buffer
        ),
    )
)


if closed_route_analysis.empty:

    st.success(
        """
        Every candidate route is selected under the
        current planning assumptions.
        """
    )

else:

    closed_route_analysis = (
        closed_route_analysis.sort_values(
            by="Best Contribution (€)",
            ascending=False,
        )
    )

    with st.expander(
        (
            "View closed candidate routes "
            f"({len(closed_route_analysis)})"
        )
    ):

        st.dataframe(
            closed_route_analysis,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Best Frequency":
                    st.column_config.NumberColumn(
                        format="%d",
                    ),

                "Best Contribution (€)":
                    st.column_config.NumberColumn(
                        format="localized",
                    ),

                "Contribution / Hour (€)":
                    st.column_config.NumberColumn(
                        format="localized",
                    ),

                "Aircraft Hours Required":
                    st.column_config.NumberColumn(
                        format="%.1f",
                    ),

                "Load Factor":
                    st.column_config.NumberColumn(
                        format="%.1f%%",
                    ),
            },
        )


# --------------------------------------------------
# Model note
# --------------------------------------------------

st.divider()

st.caption(
    """
    Route-level commercial values are modeled scenario
    assumptions. Positive standalone contribution does
    not guarantee network selection because the optimizer
    allocates limited fleet capacity across all candidate
    routes simultaneously.
    """
)