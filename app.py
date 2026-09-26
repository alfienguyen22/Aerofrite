import pandas as pd
import streamlit as st

from src.economics import calculate_route_economics
from src.optimizer import optimize_network
from src.map_utils import build_network_map

ROUTES_PATH = "data/routes.csv"
AIRPORTS_PATH = "data/airports.csv"
AIRCRAFT_PATH = "data/aircraft.csv"

# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Aerofrite Network Planner",
    page_icon="✈️",
    layout="wide",
)


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("✈️ Aerofrite Network Planner")

st.write(
    """
    Optimize Aerofrite's weekly route network from Brussels
    by allocating limited Airbus A320neo fleet capacity
    across candidate European markets.
    """
)


# --------------------------------------------------
# Sidebar controls
# --------------------------------------------------

st.sidebar.header("Planning Controls")

fleet_size = st.sidebar.slider(
    "Fleet size",
    min_value=0,
    max_value=10,
    value=5,
    step=1,
    help=(
        "Number of Airbus A320neo aircraft "
        "available to Aerofrite."
    ),
)


# --------------------------------------------------
# Run optimizer
# --------------------------------------------------

result = optimize_network(
    fleet_size_override=fleet_size,
    save_output=False,
    print_results=False,
)


# --------------------------------------------------
# Extract results
# --------------------------------------------------

active_routes = result[
    "active_routes"
].copy()

all_routes = result[
    "routes"
].copy()

# --------------------------------------------------
# Add route and airport reference data
# --------------------------------------------------

route_reference = pd.read_csv(
    ROUTES_PATH
)

airport_reference = pd.read_csv(
    AIRPORTS_PATH
)

aircraft_reference = pd.read_csv(
    AIRCRAFT_PATH
)

seats = int(
    aircraft_reference.iloc[0]["seats"]
)

route_details = active_routes.merge(
    route_reference[
        [
            "route_id",
            "destination",
            "distance_km",
            "weekly_demand",
        ]
    ],
    on="route_id",
    how="left",
)

route_details = route_details.merge(
    airport_reference[
        [
            "iata",
            "name",
            "city",
        ]
    ],
    left_on="destination",
    right_on="iata",
    how="left",
)

route_details = route_details.rename(
    columns={
        "name": "airport_name",
    }
)

if not route_details.empty:

    route_details[
        "base_demand_capture"
    ] = (
        route_details["passengers"]
        / route_details["weekly_demand"]
    )

# --------------------------------------------------
# Analyze closed routes
# --------------------------------------------------

closed_route_ids = set(
    all_routes[
        all_routes["frequency"] == 0
    ]["route_id"]
)

closed_analysis_rows = []

for _, route in route_reference.iterrows():

    route_id = route["route_id"]

    if route_id not in closed_route_ids:
        continue

    allowed_frequencies = [
        int(value)
        for value in str(
            route["frequency_options"]
        ).split("|")
        if int(value) > 0
    ]

    route_options = []

    for frequency in allowed_frequencies:

        economics = calculate_route_economics(
            route=route,
            frequency=frequency,
            seats=seats,
        )

        route_options.append(
            economics
        )

    best_option = max(
        route_options,
        key=lambda option:
        option["contribution"],
    )

    destination = route["destination"]

    airport_match = airport_reference[
        airport_reference["iata"]
        == destination
    ]

    if airport_match.empty:
        city = destination
    else:
        city = airport_match.iloc[0]["city"]

    if fleet_size == 0:

        reason = "No fleet capacity"

    elif best_option["contribution"] <= 0:

        reason = (
            "Unprofitable at all tested "
            "operating frequencies"
        )

    else:

        reason = (
            "Profitable standalone, but not "
            "selected in optimal fleet allocation"
        )

    closed_analysis_rows.append(
        {
            "Route": route_id,
            "Destination": city,
            "Market Type": route[
                "market_type"
            ],
            "Best Frequency": best_option[
                "frequency"
            ],
            "Best Contribution (€)": best_option[
                "contribution"
            ],
            "Contribution / Hour (€)": best_option[
                "contribution_per_aircraft_hour"
            ],
            "Aircraft Hours Required": best_option[
                "aircraft_hours"
            ],
            "Load Factor": (
                best_option["load_factor"]
                * 100
            ),
            "Reason": reason,
        }
    )

closed_route_analysis = pd.DataFrame(
    closed_analysis_rows
)
# --------------------------------------------------
# Network summary
# --------------------------------------------------

st.subheader("Network Summary")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Destinations Served",
    result["destinations_served"],
)

col2.metric(
    "Weekly Passengers",
    f"{int(result['total_passengers']):,}",
)

col3.metric(
    "Weekly Contribution",
    f"€{result['total_contribution']:,.0f}",
)

col4.metric(
    "Fleet Utilization",
    f"{result['fleet_utilization']:.1%}",
)


# --------------------------------------------------
# Additional metrics
# --------------------------------------------------

col5, col6, col7 = st.columns(3)

col5.metric(
    "Weekly Revenue",
    f"€{result['total_revenue']:,.0f}",
)

col6.metric(
    "Weekly Cost",
    f"€{result['total_cost']:,.0f}",
)

col7.metric(
    "Aircraft Hours",
    (
        f"{result['total_aircraft_hours']:.1f} "
        f"/ "
        f"{result['available_aircraft_hours']:.1f}"
    ),
)

# --------------------------------------------------
# Network visualizations
# --------------------------------------------------

st.subheader("Network Visuals")

if active_routes.empty:

    st.info(
        "Increase the fleet size to see "
        "network visualizations."
    )

else:

    chart_col1, chart_col2 = st.columns(2)

    # ----------------------------------------------
    # Contribution by route
    # ----------------------------------------------

    with chart_col1:

        st.markdown(
            "**Weekly Contribution by Route**"
        )

        contribution_chart = active_routes[
            [
                "route_id",
                "contribution",
            ]
        ].copy()

        contribution_chart = (
            contribution_chart.sort_values(
                by="contribution",
                ascending=False,
            )
        )

        contribution_chart = (
            contribution_chart.set_index(
                "route_id"
            )
        )

        st.bar_chart(
            contribution_chart,
        )

    # ----------------------------------------------
    # Load factor by route
    # ----------------------------------------------

    with chart_col2:

        st.markdown(
            "**Load Factor by Route**"
        )

        load_factor_chart = active_routes[
            [
                "route_id",
                "load_factor",
            ]
        ].copy()

        load_factor_chart[
            "load_factor"
        ] = (
            load_factor_chart[
                "load_factor"
            ]
            * 100
        )

        load_factor_chart = (
            load_factor_chart.sort_values(
                by="load_factor",
                ascending=False,
            )
        )

        load_factor_chart = (
            load_factor_chart.set_index(
                "route_id"
            )
        )

        st.bar_chart(
            load_factor_chart,
        )

# --------------------------------------------------
# Network map
# --------------------------------------------------

st.subheader("Optimized Route Network")

network_map = build_network_map(
    active_routes
)

st.pydeck_chart(
    network_map,
    use_container_width=True,
)

st.caption(
    "Route colors: 🔵 Business   🟣 Mixed   🔴 Leisure   "
    "• Line thickness represents weekly frequency."
)

# --------------------------------------------------
# Route inspector
# --------------------------------------------------

st.subheader("Route Inspector")

if route_details.empty:

    st.info(
        "No active routes are available to inspect."
    )

else:

    route_options = (
        route_details[
            "route_id"
        ]
        .sort_values()
        .tolist()
    )

    selected_route_id = st.selectbox(
        "Select a route",
        options=route_options,
    )

    selected_route = (
        route_details[
            route_details["route_id"]
            == selected_route_id
        ]
        .iloc[0]
    )

    st.markdown(
        f"### {selected_route['route_id']} — "
        f"{selected_route['city']}"
    )

    st.caption(
        f"{selected_route['airport_name']} • "
        f"{selected_route['distance_km']:,.0f} km from Brussels"
    )

    inspect_col1, inspect_col2, inspect_col3 = (
        st.columns(3)
    )

    inspect_col1.metric(
        "Weekly Frequency",
        f"{int(selected_route['frequency'])}x",
    )

    inspect_col2.metric(
        "Passengers",
        f"{int(selected_route['passengers']):,}",
    )

    inspect_col3.metric(
        "Load Factor",
        f"{selected_route['load_factor']:.1%}",
    )

    inspect_col4, inspect_col5, inspect_col6 = (
        st.columns(3)
    )

    inspect_col4.metric(
        "Weekly Contribution",
        f"€{selected_route['contribution']:,.0f}",
    )

    inspect_col5.metric(
        "Contribution / Aircraft Hour",
        (
            f"€"
            f"{selected_route['contribution_per_aircraft_hour']:,.0f}"
        ),
    )

    inspect_col6.metric(
        "Aircraft Hours",
        f"{selected_route['aircraft_hours']:.1f}",
    )

    st.markdown("**Demand Profile**")

    demand_col1, demand_col2, demand_col3 = (
        st.columns(3)
    )

    demand_col1.metric(
        "Base Weekly Demand",
        f"{int(selected_route['weekly_demand']):,}",
    )

    demand_col2.metric(
        "Effective Demand",
        f"{int(selected_route['effective_demand']):,}",
    )

    demand_col3.metric(
        "Base Demand Captured",
        f"{selected_route['base_demand_capture']:.1%}",
    )

    st.caption(
        "Effective demand reflects Aerofrite's modeled "
        "frequency-sensitive market capture."
    )

# --------------------------------------------------
# Active route table
# --------------------------------------------------

st.subheader("Selected Network")

if route_details.empty:

    st.warning(
        "No routes can be operated with the "
        "current fleet size."
    )

else:

    display_routes = route_details[
        [
            "route_id",
            "city",
            "market_type",
            "distance_km",
            "frequency",
            "weekly_demand",
            "effective_demand",
            "passengers",
            "load_factor",
            "revenue",
            "total_cost",
            "contribution",
            "contribution_per_aircraft_hour",
            "aircraft_hours",
        ]
    ].copy()

    display_routes = display_routes.rename(
        columns={
            "route_id": "Route",
            "city": "Destination",
            "market_type": "Market Type",
            "distance_km": "Distance (km)",
            "frequency": "Weekly Frequency",
            "weekly_demand": "Base Demand",
            "effective_demand": "Effective Demand",
            "passengers": "Passengers",
            "load_factor": "Load Factor",
            "revenue": "Revenue (€)",
            "total_cost": "Cost (€)",
            "contribution": "Contribution (€)",
            "contribution_per_aircraft_hour": (
                "Contribution / Hour (€)"
            ),
            "aircraft_hours": "Aircraft Hours",
        }
    )

    # Keep load factor numeric so sorting works.
    display_routes["Load Factor"] = (
        display_routes["Load Factor"] * 100
    )

    # Highest-contribution routes first by default.
    display_routes = (
        display_routes.sort_values(
            by="Contribution (€)",
            ascending=False,
        )
    )

    st.dataframe(
        display_routes,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Route": st.column_config.TextColumn(
                "Route",
            ),
            "Destination": st.column_config.TextColumn(
                "Destination",
            ),
            "Market Type": st.column_config.TextColumn(
                "Market Type",
            ),
            "Distance (km)": st.column_config.NumberColumn(
                "Distance (km)",
                format="%.0f",
            ),
            "Weekly Frequency": st.column_config.NumberColumn(
                "Weekly Frequency",
                format="%d",
            ),
            "Base Demand": st.column_config.NumberColumn(
                "Base Demand",
                format="%d",
            ),
            "Effective Demand": st.column_config.NumberColumn(
                "Effective Demand",
                format="%d",
            ),
            "Passengers": st.column_config.NumberColumn(
                "Passengers",
                format="%d",
            ),
            "Load Factor": st.column_config.NumberColumn(
                "Load Factor",
                format="%.1f%%",
            ),
            "Revenue (€)": st.column_config.NumberColumn(
                "Revenue (€)",
                format="localized",
            ),
            "Cost (€)": st.column_config.NumberColumn(
                "Cost (€)",
                format="localized",
            ),
            "Contribution (€)": st.column_config.NumberColumn(
                "Contribution (€)",
                format="localized",
            ),
            "Contribution / Hour (€)":
                st.column_config.NumberColumn(
                    "Contribution / Hour (€)",
                    format="localized",
                ),
            "Aircraft Hours":
                st.column_config.NumberColumn(
                    "Aircraft Hours",
                    format="%.1f",
                ),
        },
    )

# --------------------------------------------------
# Closed route analysis
# --------------------------------------------------

with st.expander(
    "Why are some candidate routes closed?"
):

    st.write(
        """
        A closed route is not necessarily
        unprofitable. Some routes generate
        positive contribution individually
        but are excluded because limited
        aircraft capacity produces more value
        elsewhere in the network.
        """
    )

    if closed_route_analysis.empty:

        st.success(
            "All candidate routes are currently "
            "included in the optimized network."
        )

    else:

        closed_route_analysis = (
            closed_route_analysis.sort_values(
                by="Best Contribution (€)",
                ascending=False,
            )
        )

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
    Aerofrite is a fictional airline planning model.
    Commercial demand, fares and costs are modeled
    assumptions rather than forecasts of actual
    airline financial performance.
    """
)