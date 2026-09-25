import streamlit as st

from src.optimizer import optimize_network


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
# Active route table
# --------------------------------------------------

st.subheader("Selected Network")

if active_routes.empty:

    st.warning(
        "No routes can be operated with the "
        "current fleet size."
    )

else:

    display_routes = active_routes[
        [
            "route_id",
            "market_type",
            "frequency",
            "passengers",
            "load_factor",
            "revenue",
            "total_cost",
            "contribution",
            "aircraft_hours",
        ]
    ].copy()

    display_routes = display_routes.rename(
        columns={
            "route_id": "Route",
            "market_type": "Market Type",
            "frequency": "Weekly Frequency",
            "passengers": "Passengers",
            "load_factor": "Load Factor",
            "revenue": "Revenue (€)",
            "total_cost": "Cost (€)",
            "contribution": "Contribution (€)",
            "aircraft_hours": "Aircraft Hours",
        }
    )

    # Convert load factor from decimal form
    # such as 0.952 to percentage form 95.2.
    # It remains numeric so sorting still works.
    display_routes["Load Factor"] = (
        display_routes["Load Factor"]
        * 100
    )

    # Sort highest contribution first by default.
    # Users can still click any column header
    # to sort interactively.
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
            "Market Type": st.column_config.TextColumn(
                "Market Type",
            ),
            "Weekly Frequency": st.column_config.NumberColumn(
                "Weekly Frequency",
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
            "Aircraft Hours": st.column_config.NumberColumn(
                "Aircraft Hours",
                format="%.1f",
            ),
        },
    )


# --------------------------------------------------
# Closed routes
# --------------------------------------------------

with st.expander(
    "View closed candidate routes"
):

    closed_routes = all_routes[
        all_routes["frequency"] == 0
    ][
        [
            "route_id",
            "market_type",
        ]
    ].copy()

    closed_routes = closed_routes.rename(
        columns={
            "route_id": "Route",
            "market_type": "Market Type",
        }
    )

    closed_routes = closed_routes.sort_values(
        by="Route"
    )

    st.dataframe(
        closed_routes,
        use_container_width=True,
        hide_index=True,
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