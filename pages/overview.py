import streamlit as st

from src.app_state import (
    get_planning_state,
)
from src.app_services import (
    build_route_details,
    get_optimized_network,
)
from src.map_utils import (
    build_network_map,
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
# Optimize current network
# --------------------------------------------------

with st.spinner(
    "Optimizing network..."
):

    result = get_optimized_network(
        fleet_size=fleet_size,
        season=season,
        operational_buffer=(
            operational_buffer
        ),
    )


active_routes = result[
    "active_routes"
].copy()

route_details = build_route_details(
    result["routes"],
    active_only=True,
)


# --------------------------------------------------
# Header
# --------------------------------------------------

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
# Headline network metrics
# --------------------------------------------------

metric1, metric2, metric3, metric4 = (
    st.columns(4)
)

metric1.metric(
    "Destinations",
    result[
        "destinations_served"
    ],
)

metric2.metric(
    "Weekly Passengers",
    (
        f"{int(result['total_passengers']):,}"
    ),
)

metric3.metric(
    "Weekly Contribution",
    (
        f"€"
        f"{result['total_contribution']:,.0f}"
    ),
)

metric4.metric(
    "Planning Utilization",
    (
        f"{result['fleet_utilization']:.1%}"
    ),
)


# --------------------------------------------------
# Fleet capacity summary
# --------------------------------------------------

st.markdown(
    "**Fleet Capacity**"
)

capacity1, capacity2, capacity3, (
    capacity4
) = st.columns(4)

capacity1.metric(
    "Theoretical Capacity",
    (
        f"{result['theoretical_aircraft_hours']:.1f} h"
    ),
)

capacity2.metric(
    "Operational Reserve",
    (
        f"{result['reserved_aircraft_hours']:.1f} h"
    ),
)

capacity3.metric(
    "Planning Capacity",
    (
        f"{result['available_aircraft_hours']:.1f} h"
    ),
)

capacity4.metric(
    "Scheduled Hours",
    (
        f"{result['total_aircraft_hours']:.1f} h"
    ),
)


# --------------------------------------------------
# Network map
# --------------------------------------------------

st.subheader(
    "Optimized Route Network"
)

if active_routes.empty:

    st.info(
        """
        No routes can be operated under the
        current planning assumptions.
        """
    )

else:

    network_map = build_network_map(
        active_routes
    )

    st.pydeck_chart(
        network_map,
        use_container_width=True,
    )

    st.caption(
        """
        Route colors: 🔵 Business   🟣 Mixed   🔴 Leisure
        • Line thickness represents weekly frequency.
        """
    )


# --------------------------------------------------
# Network visuals
# --------------------------------------------------

st.subheader(
    "Network Performance"
)

if active_routes.empty:

    st.info(
        """
        Increase available fleet capacity to see
        network performance charts.
        """
    )

else:

    chart_col1, chart_col2 = (
        st.columns(2)
    )

    # ----------------------------------------------
    # Contribution by route
    # ----------------------------------------------

    with chart_col1:

        st.markdown(
            "**Weekly Contribution by Route**"
        )

        contribution_chart = (
            active_routes[
                [
                    "route_id",
                    "contribution",
                ]
            ]
            .sort_values(
                by="contribution",
                ascending=False,
            )
            .set_index(
                "route_id"
            )
        )

        st.bar_chart(
            contribution_chart
        )

    # ----------------------------------------------
    # Load factor by route
    # ----------------------------------------------

    with chart_col2:

        st.markdown(
            "**Load Factor by Route**"
        )

        load_factor_chart = (
            active_routes[
                [
                    "route_id",
                    "load_factor",
                ]
            ]
            .copy()
        )

        load_factor_chart[
            "load_factor"
        ] = (
            load_factor_chart[
                "load_factor"
            ]
            * 100
        )

        load_factor_chart = (
            load_factor_chart
            .sort_values(
                by="load_factor",
                ascending=False,
            )
            .set_index(
                "route_id"
            )
        )

        st.bar_chart(
            load_factor_chart
        )


# --------------------------------------------------
# Selected network table
# --------------------------------------------------

st.subheader(
    "Selected Network"
)

if route_details.empty:

    st.warning(
        """
        No routes are selected under the
        current planning assumptions.
        """
    )

else:

    display_routes = route_details[
        [
            "route_id",
            "city",
            "market_type",
            "frequency",
            "passengers",
            "load_factor",
            "contribution",
            "aircraft_hours",
        ]
    ].copy()

    display_routes = (
        display_routes.rename(
            columns={
                "route_id":
                    "Route",

                "city":
                    "Destination",

                "market_type":
                    "Market Type",

                "frequency":
                    "Weekly Frequency",

                "passengers":
                    "Passengers",

                "load_factor":
                    "Load Factor",

                "contribution":
                    "Contribution (€)",

                "aircraft_hours":
                    "Aircraft Hours",
            }
        )
    )

    display_routes[
        "Market Type"
    ] = (
        display_routes[
            "Market Type"
        ]
        .str.title()
    )

    display_routes[
        "Load Factor"
    ] = (
        display_routes[
            "Load Factor"
        ]
        * 100
    )

    display_routes = (
        display_routes.sort_values(
            by="Contribution (€)",
            ascending=False,
        )
    )

    with st.expander(
        "View selected network table"
    ):

        st.dataframe(
            display_routes,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Weekly Frequency":
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

                "Aircraft Hours":
                    st.column_config.NumberColumn(
                        format="%.1f",
                    ),
            },
        )


# --------------------------------------------------
# Model note
# --------------------------------------------------

st.divider()

st.caption(
    """
    Aerofrite is a fictional airline planning model.
    Commercial demand, fare, competition, seasonality,
    cost, and operational-reserve inputs are simplified
    scenario assumptions rather than forecasts of
    actual airline performance.
    """
)