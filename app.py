import pandas as pd
import streamlit as st

from src.scenarios import (
    compare_fleet_scenarios,
    compare_networks,
)
from src.economics import calculate_route_economics
from src.optimizer import optimize_network
from src.map_utils import build_network_map
from src.demand import (
    build_frequency_curve,
    calculate_effective_demand,
)

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
# Fleet scenario comparison
# --------------------------------------------------

st.subheader("Fleet Scenario Comparison")

st.write(
    """
    Compare alternative fleet sizes to understand
    how additional aircraft capacity changes the
    optimized Aerofrite network.
    """
)

scenario_fleet_sizes = [
    4,
    5,
    6,
]

scenario_summary, scenario_results = (
    compare_fleet_scenarios(
        scenario_fleet_sizes
    )
)


# --------------------------------------------------
# Scenario summary table
# --------------------------------------------------

st.markdown(
    "**Scenario Summary**"
)

scenario_display = (
    scenario_summary.copy()
)

st.dataframe(
    scenario_display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Fleet Size":
            st.column_config.NumberColumn(
                "Fleet Size",
                format="%d",
            ),
        "Destinations":
            st.column_config.NumberColumn(
                "Destinations",
                format="%d",
            ),
        "Passengers":
            st.column_config.NumberColumn(
                "Passengers",
                format="%d",
            ),
        "Revenue (€)":
            st.column_config.NumberColumn(
                "Revenue (€)",
                format="localized",
            ),
        "Cost (€)":
            st.column_config.NumberColumn(
                "Cost (€)",
                format="localized",
            ),
        "Contribution (€)":
            st.column_config.NumberColumn(
                "Contribution (€)",
                format="localized",
            ),
        "Aircraft Hours":
            st.column_config.NumberColumn(
                "Aircraft Hours",
                format="%.1f",
            ),
        "Available Hours":
            st.column_config.NumberColumn(
                "Available Hours",
                format="%.1f",
            ),
        "Utilization":
            st.column_config.NumberColumn(
                "Utilization",
                format="%.1f%%",
            ),
        "Incremental Contribution (€)":
            st.column_config.NumberColumn(
                "Incremental Contribution (€)",
                format="localized",
            ),
        "Incremental Passengers":
            st.column_config.NumberColumn(
                "Incremental Passengers",
                format="%.0f",
            ),
        "Incremental Destinations":
            st.column_config.NumberColumn(
                "Incremental Destinations",
                format="%.0f",
            ),
    },
)

# --------------------------------------------------
# Fleet expansion analysis
# --------------------------------------------------

st.markdown(
    "**Fleet Expansion Value**"
)

chart_col1, chart_col2 = st.columns(2)


# --------------------------------------------------
# Contribution by fleet size
# --------------------------------------------------

with chart_col1:

    st.markdown(
        "##### Modeled Weekly Contribution"
    )

    contribution_chart = (
        scenario_summary[
            [
                "Fleet Size",
                "Contribution (€)",
            ]
        ]
        .set_index("Fleet Size")
    )

    st.bar_chart(
        contribution_chart
    )


# --------------------------------------------------
# Passengers by fleet size
# --------------------------------------------------

with chart_col2:

    st.markdown(
        "##### Modeled Weekly Passengers"
    )

    passenger_chart = (
        scenario_summary[
            [
                "Fleet Size",
                "Passengers",
            ]
        ]
        .set_index("Fleet Size")
    )

    st.bar_chart(
        passenger_chart
    )

# --------------------------------------------------
# Incremental aircraft value
# --------------------------------------------------

st.markdown(
    "**Incremental Value of Additional Aircraft**"
)

incremental_rows = (
    scenario_summary[
        scenario_summary[
            "Incremental Contribution (€)"
        ].notna()
    ]
)

incremental_cols = st.columns(
    len(incremental_rows)
)

for column, (_, row) in zip(
    incremental_cols,
    incremental_rows.iterrows(),
):

    fleet_size_value = int(
        row["Fleet Size"]
    )

    previous_fleet_size = (
        fleet_size_value - 1
    )

    with column:

        st.markdown(
            f"##### "
            f"{previous_fleet_size} → "
            f"{fleet_size_value} Aircraft"
        )

        st.metric(
            "Additional Contribution",
            (
                f"€"
                f"{row['Incremental Contribution (€)']:,.0f}"
            ),
        )

        st.metric(
            "Additional Passengers",
            (
                f"+"
                f"{row['Incremental Passengers']:,.0f}"
            ),
        )

        st.metric(
            "Additional Destinations",
            (
                f"+"
                f"{row['Incremental Destinations']:,.0f}"
            ),
        )

        st.metric(
            "Contribution / Added Hour",
            (
                f"€"
                f"{row['Incremental Contribution / Hour (€)']:,.0f}"
            ),
        )

st.caption(
    """
    Incremental values compare adjacent optimized fleet scenarios.
    Lower marginal contribution at higher fleet sizes can indicate
    diminishing value from additional modeled capacity.
    """
)

# --------------------------------------------------
# Choose two scenarios to compare
# --------------------------------------------------

st.markdown(
    "**Compare Two Fleet Plans**"
)

scenario_col1, scenario_col2 = (
    st.columns(2)
)

with scenario_col1:

    baseline_fleet = st.selectbox(
        "Baseline fleet",
        options=scenario_fleet_sizes,
        index=1,
        key="baseline_fleet",
    )

with scenario_col2:

    alternative_fleet = st.selectbox(
        "Alternative fleet",
        options=scenario_fleet_sizes,
        index=2,
        key="alternative_fleet",
    )


# --------------------------------------------------
# Pull summary rows
# --------------------------------------------------

baseline_summary = (
    scenario_summary[
        scenario_summary["Fleet Size"]
        == baseline_fleet
    ]
    .iloc[0]
)

alternative_summary = (
    scenario_summary[
        scenario_summary["Fleet Size"]
        == alternative_fleet
    ]
    .iloc[0]
)


# --------------------------------------------------
# Calculate changes
# --------------------------------------------------

contribution_change = (
    alternative_summary[
        "Contribution (€)"
    ]
    - baseline_summary[
        "Contribution (€)"
    ]
)

passenger_change = (
    alternative_summary[
        "Passengers"
    ]
    - baseline_summary[
        "Passengers"
    ]
)

destination_change = (
    alternative_summary[
        "Destinations"
    ]
    - baseline_summary[
        "Destinations"
    ]
)

aircraft_hour_change = (
    alternative_summary[
        "Aircraft Hours"
    ]
    - baseline_summary[
        "Aircraft Hours"
    ]
)


# --------------------------------------------------
# Incremental value metrics
# --------------------------------------------------

st.markdown(
    f"**Modeled Impact: {baseline_fleet} → "
    f"{alternative_fleet} Aircraft**"
)

impact_col1, impact_col2, (
    impact_col3
), impact_col4 = st.columns(4)

contribution_change_display = (
    f"+€{contribution_change:,.0f}"
    if contribution_change > 0
    else (
        f"-€{abs(contribution_change):,.0f}"
        if contribution_change < 0
        else "€0"
    )
)

impact_col1.metric(
    "Contribution Change",
    contribution_change_display,
)

impact_col2.metric(
    "Passenger Change",
    f"{passenger_change:+,.0f}",
)

impact_col3.metric(
    "Destination Change",
    f"{destination_change:+,.0f}",
)

impact_col4.metric(
    "Aircraft Hours Change",
    f"{aircraft_hour_change:+.1f}",
)


# --------------------------------------------------
# Network changes
# --------------------------------------------------

st.markdown(
    "**Network Changes**"
)

network_changes = compare_networks(
    scenario_results[
        baseline_fleet
    ],
    scenario_results[
        alternative_fleet
    ],
)

if network_changes.empty:

    st.info(
        "The selected scenarios produce "
        "the same route frequencies."
    )

else:

    st.dataframe(
        network_changes,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Route":
                st.column_config.TextColumn(
                    "Route",
                ),
            "Frequency A":
                st.column_config.NumberColumn(
                    (
                        f"{baseline_fleet} "
                        "Aircraft"
                    ),
                    format="%d",
                ),
            "Frequency B":
                st.column_config.NumberColumn(
                    (
                        f"{alternative_fleet} "
                        "Aircraft"
                    ),
                    format="%d",
                ),
            "Frequency Change":
                st.column_config.NumberColumn(
                    "Change",
                    format="%+d",
                ),
            "Change Type":
                st.column_config.TextColumn(
                    "Change Type",
                ),
        },
    )
# --------------------------------------------------
# Demand model explorer
# --------------------------------------------------

st.subheader("Demand Model Explorer")

st.write(
    """
    Aerofrite models passenger demand as frequency-sensitive.
    Business markets are assumed to respond more strongly to
    increased flight frequency than leisure markets, while mixed
    markets sit between the two.
    """
)


# --------------------------------------------------
# Build frequency-response data
# --------------------------------------------------

frequency_curve = pd.DataFrame(
    build_frequency_curve()
)


# --------------------------------------------------
# Demand capture curve
# --------------------------------------------------

st.markdown(
    "**Modeled Demand Capture by Weekly Frequency**"
)

capture_chart = (
    frequency_curve.pivot(
        index="Weekly Frequency",
        columns="Market Type",
        values="Demand Capture (%)",
    )
    .rename(
        columns={
            "business": "Business",
            "mixed": "Mixed",
            "leisure": "Leisure",
        }
    )
)

st.line_chart(
    capture_chart
)

st.caption(
    """
    Seven weekly flights represent the baseline demand level
    of 100%. Values above 100% represent additional modeled
    market capture from offering more frequent service.
    """
)

# --------------------------------------------------
# Interactive demand example
# --------------------------------------------------

st.markdown(
    "**Explore a Hypothetical Market**"
)

explorer_col1, explorer_col2 = st.columns(2)

with explorer_col1:

    explorer_market_type = st.selectbox(
        "Market type",
        options=[
            "business",
            "mixed",
            "leisure",
        ],
        index=1,
        key="demand_market_type",
    )

with explorer_col2:

    explorer_base_demand = st.slider(
        "Base weekly demand",
        min_value=500,
        max_value=5000,
        value=2000,
        step=100,
        key="demand_base_demand",
    )

# --------------------------------------------------
# Calculate frequency-sensitive demand
# --------------------------------------------------

explorer_frequencies = [
    0,
    3,
    4,
    7,
    10,
    14,
]

explorer_rows = []

for frequency in explorer_frequencies:

    effective_demand = (
        calculate_effective_demand(
            base_weekly_demand=(
                explorer_base_demand
            ),
            market_type=(
                explorer_market_type
            ),
            frequency=frequency,
        )
    )

    explorer_rows.append(
        {
            "Weekly Frequency":
                frequency,
            "Effective Demand":
                effective_demand,
            "Demand Capture (%)":
                (
                    effective_demand
                    / explorer_base_demand
                    * 100
                ),
        }
    )

explorer_demand = pd.DataFrame(
    explorer_rows
)

st.markdown(
    f"**Effective Demand — "
    f"{explorer_market_type.title()} Market**"
)

effective_demand_chart = (
    explorer_demand[
        [
            "Weekly Frequency",
            "Effective Demand",
        ]
    ]
    .set_index(
        "Weekly Frequency"
    )
)

st.bar_chart(
    effective_demand_chart
)

# --------------------------------------------------
# Key frequency examples
# --------------------------------------------------

freq_3_demand = (
    calculate_effective_demand(
        base_weekly_demand=(
            explorer_base_demand
        ),
        market_type=(
            explorer_market_type
        ),
        frequency=3,
    )
)

freq_7_demand = (
    calculate_effective_demand(
        base_weekly_demand=(
            explorer_base_demand
        ),
        market_type=(
            explorer_market_type
        ),
        frequency=7,
    )
)

freq_14_demand = (
    calculate_effective_demand(
        base_weekly_demand=(
            explorer_base_demand
        ),
        market_type=(
            explorer_market_type
        ),
        frequency=14,
    )
)

demand_metric1, demand_metric2, (
    demand_metric3
) = st.columns(3)

demand_metric1.metric(
    "3x Weekly",
    f"{freq_3_demand:,} passengers",
)

demand_metric2.metric(
    "Daily",
    f"{freq_7_demand:,} passengers",
)

demand_metric3.metric(
    "2x Daily",
    f"{freq_14_demand:,} passengers",
)

with st.expander(
    "View demand model assumptions"
):

    assumption_table = (
        frequency_curve[
            [
                "Market Type",
                "Weekly Frequency",
                "Demand Capture (%)",
            ]
        ]
        .copy()
    )

    assumption_table[
        "Market Type"
    ] = (
        assumption_table[
            "Market Type"
        ]
        .str.title()
    )

    st.dataframe(
        assumption_table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Weekly Frequency":
                st.column_config.NumberColumn(
                    format="%d",
                ),
            "Demand Capture (%)":
                st.column_config.NumberColumn(
                    format="%.0f%%",
                ),
        },
    )

    st.caption(
        """
        These response factors are transparent modeling
        assumptions for Aerofrite and are not calibrated
        forecasts of observed airline passenger behavior.
        """
    )

# --------------------------------------------------
# Demand behavior in optimized network
# --------------------------------------------------

st.subheader("Demand Behavior in Optimized Network")

st.write(
    """
    The table below shows how Aerofrite's selected
    frequencies translate base market demand into
    modeled effective demand for the current
    optimized network.
    """
)

if route_details.empty:

    st.info(
        "No active routes are available "
        "for demand analysis."
    )

else:

    network_demand = route_details.copy()

    # --------------------------------------------------
    # Calculate demand-capture metrics
    # --------------------------------------------------

    network_demand[
        "frequency_demand_capture"
    ] = (
        network_demand[
            "effective_demand"
        ]
        / network_demand[
            "weekly_demand"
        ]
        * 100
    )

    network_demand[
        "passenger_capture"
    ] = (
        network_demand[
            "passengers"
        ]
        / network_demand[
            "weekly_demand"
        ]
        * 100
    )

    network_demand[
        "load_factor_percent"
    ] = (
        network_demand[
            "load_factor"
        ]
        * 100
    )


    # --------------------------------------------------
    # Network demand table
    # --------------------------------------------------

    demand_display = network_demand[
        [
            "route_id",
            "city",
            "market_type",
            "frequency",
            "weekly_demand",
            "effective_demand",
            "passengers",
            "frequency_demand_capture",
            "load_factor_percent",
        ]
    ].copy()

    demand_display = demand_display.rename(
        columns={
            "route_id": "Route",
            "city": "Destination",
            "market_type": "Market Type",
            "frequency": "Weekly Frequency",
            "weekly_demand": "Base Demand",
            "effective_demand": "Effective Demand",
            "passengers": "Passengers",
            "frequency_demand_capture":
                "Modeled Demand Capture",
            "load_factor_percent":
                "Load Factor",
        }
    )

    demand_display[
        "Market Type"
    ] = (
        demand_display[
            "Market Type"
        ]
        .str.title()
    )

    demand_display = (
        demand_display.sort_values(
            by=[
                "Market Type",
                "Weekly Frequency",
            ],
            ascending=[
                True,
                False,
            ],
        )
    )

    st.dataframe(
        demand_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Weekly Frequency":
                st.column_config.NumberColumn(
                    format="%d",
                ),
            "Base Demand":
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
            "Modeled Demand Capture":
                st.column_config.NumberColumn(
                    format="%.1f%%",
                ),
            "Load Factor":
                st.column_config.NumberColumn(
                    format="%.1f%%",
                ),
        },
    )

# --------------------------------------------------
# Summary by market type
# --------------------------------------------------

st.markdown(
    "**Frequency Strategy by Market Type**"
)

market_summary = (
    network_demand.groupby(
        "market_type"
    )
    .agg(
        routes=(
            "route_id",
            "count",
        ),
        average_frequency=(
            "frequency",
            "mean",
        ),
        average_demand_capture=(
            "frequency_demand_capture",
            "mean",
        ),
        total_passengers=(
            "passengers",
            "sum",
        ),
        average_load_factor=(
            "load_factor_percent",
            "mean",
        ),
    )
    .reset_index()
)

market_summary[
    "market_type"
] = (
    market_summary[
        "market_type"
    ]
    .str.title()
)

market_summary = market_summary.rename(
    columns={
        "market_type": "Market Type",
        "routes": "Routes",
        "average_frequency":
            "Average Frequency",
        "average_demand_capture":
            "Average Demand Capture",
        "total_passengers":
            "Passengers",
        "average_load_factor":
            "Average Load Factor",
    }
)

st.dataframe(
    market_summary,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Routes":
            st.column_config.NumberColumn(
                format="%d",
            ),
        "Average Frequency":
            st.column_config.NumberColumn(
                format="%.1f",
            ),
        "Average Demand Capture":
            st.column_config.NumberColumn(
                format="%.1f%%",
            ),
        "Passengers":
            st.column_config.NumberColumn(
                format="%d",
            ),
        "Average Load Factor":
            st.column_config.NumberColumn(
                format="%.1f%%",
            ),
    },
)

st.caption(
    """
    These patterns are outcomes of both the frequency-sensitive
    demand assumptions and the network optimization. They should
    not be interpreted as observed airline-market behavior.
    """
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