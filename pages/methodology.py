import pandas as pd
import streamlit as st

from src.app_services import (
    load_reference_data,
)
from src.demand import (
    build_frequency_curve,
)
from src.market_adjustments import (
    COMPETITION_MULTIPLIERS,
    SEASONALITY_MULTIPLIERS,
)


# --------------------------------------------------
# Reference data
# --------------------------------------------------

reference = load_reference_data()

route_reference = reference[
    "routes"
]

aircraft_reference = reference[
    "aircraft"
]

aircraft = aircraft_reference.iloc[0]

candidate_routes = len(
    route_reference
)


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title(
    "ℹ️ Methodology"
)

st.write(
    """
    Aerofrite is a strategic airline network-planning
    model that combines simplified commercial assumptions
    with mathematical optimization to allocate limited
    aircraft capacity across candidate routes.
    """
)

st.warning(
    """
    Aerofrite is a fictional airline. Commercial demand,
    fares, costs, competition, and seasonal effects are
    modeled scenario assumptions and should not be
    interpreted as forecasts of actual airline performance.
    """
)


# --------------------------------------------------
# Model overview
# --------------------------------------------------

st.subheader(
    "Model Overview"
)

st.write(
    """
    The model evaluates alternative weekly frequencies
    for each candidate route from Brussels and selects
    the combination that maximizes modeled weekly network
    contribution while respecting available aircraft-hour
    capacity.
    """
)

st.info(
    """
    Market Assumptions
    → Route Economics
    → Frequency Alternatives
    → Fleet Capacity Constraint
    → Network Optimization
    → Recommended Route Network
    """
)


overview1, overview2, overview3, (
    overview4
) = st.columns(4)

overview1.metric(
    "Hub",
    "BRU",
)

overview2.metric(
    "Candidate Routes",
    candidate_routes,
)

overview3.metric(
    "Aircraft Type",
    str(
        aircraft[
            "aircraft_type"
        ]
    ),
)

overview4.metric(
    "Seats",
    int(
        aircraft[
            "seats"
        ]
    ),
)


# --------------------------------------------------
# Optimization formulation
# --------------------------------------------------

st.subheader(
    "Network Optimization"
)

st.write(
    """
    For every candidate route, Aerofrite chooses one
    weekly round-trip frequency from a discrete set:
    """
)

st.code(
    "0, 3, 4, 7, 10, or 14 weekly round trips",
    language=None,
)

st.write(
    """
    A frequency of zero means the route remains closed.

    The optimizer considers the contribution and aircraft
    hours associated with every route-frequency combination
    and selects the network with the highest total modeled
    contribution.
    """
)


with st.expander(
    "View optimization formulation"
):

    st.markdown(
        "**Decision**"
    )

    st.write(
        """
        For each route r and allowed frequency f,
        choose whether that route-frequency combination
        is included in the network.
        """
    )

    st.markdown(
        "**Objective**"
    )

    st.latex(
        r"""
        \max
        \sum_{r}
        \sum_{f}
        Contribution_{r,f}
        \times x_{r,f}
        """
    )

    st.markdown(
        "**One frequency per route**"
    )

    st.latex(
        r"""
        \sum_f x_{r,f} = 1
        """
    )

    st.write(
        "for every candidate route."
    )

    st.markdown(
        "**Fleet-capacity constraint**"
    )

    st.latex(
        r"""
        \sum_r
        \sum_f
        AircraftHours_{r,f}
        \times x_{r,f}
        \leq
        PlanningCapacity
        """
    )

    st.write(
        """
        The model is solved as a discrete optimization
        problem using Google OR-Tools CP-SAT.
        """
    )


# --------------------------------------------------
# Fleet assumptions
# --------------------------------------------------

st.subheader(
    "Fleet Capacity"
)

fleet1, fleet2, fleet3, fleet4 = (
    st.columns(4)
)

fleet1.metric(
    "Aircraft",
    str(
        aircraft[
            "aircraft_type"
        ]
    ),
)

fleet2.metric(
    "Seats",
    int(
        aircraft[
            "seats"
        ]
    ),
)

fleet3.metric(
    "Usable Hours / Day",
    (
        f"{float(aircraft['usable_hours_per_day']):.1f}"
    ),
)

fleet4.metric(
    "Turnaround",
    (
        f"{int(aircraft['turnaround_minutes'])} min"
    ),
)


st.write(
    """
    Theoretical weekly fleet capacity is calculated as:
    """
)

st.code(
    (
        "Fleet Size "
        "× Usable Hours per Aircraft per Day "
        "× 7 Days"
    ),
    language=None,
)

st.write(
    """
    Aerofrite can then reserve a percentage of this
    theoretical capacity for simplified maintenance,
    disruption recovery, and operational flexibility.
    """
)

st.code(
    (
        "Planning Capacity = "
        "Theoretical Capacity × "
        "(1 − Operational Reserve)"
    ),
    language=None,
)

st.caption(
    """
    The operational reserve is a strategic capacity
    allowance rather than an explicit aircraft-maintenance
    or disruption-scheduling model.
    """
)


# --------------------------------------------------
# Demand methodology
# --------------------------------------------------

st.subheader(
    "Demand Methodology"
)

st.write(
    """
    Route demand passes through several transparent
    modeling stages before becoming passenger demand
    available to the network optimizer.
    """
)

st.info(
    """
    Base Weekly Demand
    → Seasonal Adjustment
    → Competition Adjustment
    → Frequency Response
    → Effective Demand
    → Seat Capacity
    → Passengers Carried
    """
)


# --------------------------------------------------
# Frequency-response assumptions
# --------------------------------------------------

with st.expander(
    "Frequency-response assumptions",
    expanded=True,
):

    frequency_curve = pd.DataFrame(
        build_frequency_curve()
    )

    frequency_table = (
        frequency_curve[
            [
                "Market Type",
                "Weekly Frequency",
                "Demand Capture (%)",
            ]
        ]
        .copy()
    )

    frequency_table[
        "Market Type"
    ] = (
        frequency_table[
            "Market Type"
        ]
        .str.title()
    )

    st.dataframe(
        frequency_table,
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

    st.write(
        """
        Seven weekly round trips represent the baseline
        frequency response of 100%.

        Business markets are modeled as more sensitive to
        low frequency than leisure markets because schedule
        convenience is assumed to matter more strongly for
        business-oriented demand.
        """
    )


# --------------------------------------------------
# Competition assumptions
# --------------------------------------------------

with st.expander(
    "Competition assumptions"
):

    competition_rows = []

    for (
        competition_level,
        multiplier,
    ) in COMPETITION_MULTIPLIERS.items():

        competition_rows.append(
            {
                "Competition Level":
                    competition_level.title(),

                "Demand Multiplier":
                    multiplier * 100,
            }
        )

    competition_table = pd.DataFrame(
        competition_rows
    )

    st.dataframe(
        competition_table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Demand Multiplier":
                st.column_config.NumberColumn(
                    format="%.0f%%",
                ),
        },
    )

    st.write(
        """
        Competition categories represent simplified
        modeled competitive intensity.

        They are not based on live airline schedules,
        observed market share, or competitor capacity.
        """
    )


# --------------------------------------------------
# Seasonality assumptions
# --------------------------------------------------

with st.expander(
    "Seasonality assumptions"
):

    seasonality_rows = []

    for (
        market_type,
        season_values,
    ) in SEASONALITY_MULTIPLIERS.items():

        for (
            season_name,
            multiplier,
        ) in season_values.items():

            seasonality_rows.append(
                {
                    "Market Type":
                        market_type.title(),

                    "Season":
                        season_name.title(),

                    "Demand Multiplier":
                        multiplier * 100,
                }
            )

    seasonality = pd.DataFrame(
        seasonality_rows
    )

    seasonality_table = (
        seasonality.pivot(
            index="Market Type",
            columns="Season",
            values="Demand Multiplier",
        )
        .reset_index()
    )

    season_columns = [
        column
        for column in [
            "Winter",
            "Shoulder",
            "Summer",
        ]
        if column
        in seasonality_table.columns
    ]

    seasonality_table = (
        seasonality_table[
            [
                "Market Type",
                *season_columns,
            ]
        ]
    )

    st.dataframe(
        seasonality_table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Winter":
                st.column_config.NumberColumn(
                    format="%.0f%%",
                ),

            "Shoulder":
                st.column_config.NumberColumn(
                    format="%.0f%%",
                ),

            "Summer":
                st.column_config.NumberColumn(
                    format="%.0f%%",
                ),
        },
    )

    st.write(
        """
        Leisure markets receive the strongest modeled
        summer uplift, mixed markets receive a smaller
        summer uplift, and business markets are modeled
        as comparatively stable across seasons.
        """
    )


# --------------------------------------------------
# Passenger calculation
# --------------------------------------------------

with st.expander(
    "Passenger-demand calculation"
):

    st.write(
        "For a route:"
    )

    st.latex(
        r"""
        AdjustedDemand =
        BaseDemand
        \times SeasonalMultiplier
        \times CompetitionMultiplier
        """
    )

    st.write(
        """
        The frequency-response multiplier is
        then applied:
        """
    )

    st.latex(
        r"""
        EffectiveDemand =
        AdjustedDemand
        \times FrequencyMultiplier
        """
    )

    st.write(
        "Weekly seat capacity is:"
    )

    st.latex(
        r"""
        WeeklySeats =
        Frequency
        \times Seats
        \times 2
        """
    )

    st.write(
        """
        because each weekly round trip contains
        one outbound and one inbound flight.
        """
    )

    st.write(
        """
        Passengers carried are limited by both
        modeled demand and available capacity:
        """
    )

    st.latex(
        r"""
        Passengers =
        \min(
        EffectiveDemand,
        WeeklySeats
        )
        """
    )


# --------------------------------------------------
# Route economics
# --------------------------------------------------

st.subheader(
    "Route Economics"
)

st.write(
    """
    Each route-frequency alternative is evaluated using
    a simplified weekly contribution model.
    """
)


with st.expander(
    "Fare assumptions"
):

    st.write(
        """
        Aerofrite's modeled average fare begins with a
        distance-based reference fare:
        """
    )

    st.code(
        (
            "Reference Fare = "
            "€45 + (€0.065 × Distance in km)"
        ),
        language=None,
    )

    st.write(
        """
        A route-specific fare multiplier is then applied
        to represent differences in market characteristics.
        """
    )

    st.code(
        (
            "Average Fare = "
            "Reference Fare × Fare Multiplier"
        ),
        language=None,
    )

    st.caption(
        """
        Fare values are simulated commercial assumptions,
        not observed ticket-price forecasts.
        """
    )


with st.expander(
    "Operating-cost assumptions"
):

    st.write(
        """
        The simplified operating-cost model contains
        distance, block-time, airport, and route-level
        components.
        """
    )

    st.code(
        (
            "Operating Cost per Rotation =\n"
            "€2,500\n"
            "+ €2.40 × Round-Trip Distance (km)\n"
            "+ €850 × Round-Trip Block Hours"
        ),
        language=None,
    )

    st.write(
        """
        An airport-cost assumption is added according
        to the modeled airport-cost tier.
        """
    )

    airport_costs = pd.DataFrame(
        [
            {
                "Airport Cost Tier":
                    "Low",
                "Cost / Rotation (€)":
                    1500,
            },
            {
                "Airport Cost Tier":
                    "Medium",
                "Cost / Rotation (€)":
                    2000,
            },
            {
                "Airport Cost Tier":
                    "High",
                "Cost / Rotation (€)":
                    2800,
            },
        ]
    )

    st.dataframe(
        airport_costs,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Cost / Rotation (€)":
                st.column_config.NumberColumn(
                    format="localized",
                ),
        },
    )

    st.write(
        """
        Each route also has a modeled weekly fixed
        route cost.
        """
    )


with st.expander(
    "Contribution calculation"
):

    st.write(
        "Weekly revenue:"
    )

    st.latex(
        r"""
        Revenue =
        Passengers
        \times AverageFare
        """
    )

    st.write(
        "Variable weekly cost:"
    )

    st.latex(
        r"""
        VariableCost =
        Frequency
        \times VariableCostPerRotation
        """
    )

    st.write(
        "Total modeled weekly cost:"
    )

    st.latex(
        r"""
        TotalCost =
        VariableCost
        + WeeklyFixedRouteCost
        """
    )

    st.write(
        "Route contribution:"
    )

    st.latex(
        r"""
        Contribution =
        Revenue
        - TotalCost
        """
    )

    st.write(
        """
        Aerofrite's optimization objective maximizes
        the sum of this modeled contribution across
        the selected network.
        """
    )

    st.warning(
        """
        Contribution is a simplified planning metric.
        It should not be interpreted as accounting
        profit, operating profit, EBIT, or net income.
        """
    )


# --------------------------------------------------
# Geography and route construction
# --------------------------------------------------

st.subheader(
    "Route Construction"
)

with st.expander(
    "Airport, distance, and block-time methodology"
):

    st.write(
        """
        Airport names, coordinates, and reference metadata
        are based on the project's airport dataset derived
        from OurAirports.
        """
    )

    st.write(
        """
        Great-circle route distance is calculated using
        the Haversine formula.
        """
    )

    st.code(
        (
            "One-Way Block Hours = "
            "Distance / 750 + 0.55"
        ),
        language=None,
    )

    st.code(
        (
            "Round-Trip Block Hours = "
            "2 × One-Way Block Hours "
            "+ 2 × Turnaround Time"
        ),
        language=None,
    )

    st.write(
        (
            f"The modeled "
            f"{aircraft['aircraft_type']} "
            f"has a planning range of "
            f"{float(aircraft['planning_range_km']):,.0f} km."
        )
    )


# --------------------------------------------------
# What is real vs modeled
# --------------------------------------------------

st.subheader(
    "Data Classification"
)

classification = pd.DataFrame(
    [
        {
            "Input":
                "Airport coordinates",
            "Classification":
                "Reference data",
        },
        {
            "Input":
                "Airport names / codes",
            "Classification":
                "Reference data",
        },
        {
            "Input":
                "Route distance",
            "Classification":
                "Calculated from airport coordinates",
        },
        {
            "Input":
                "Aircraft type / seats / range",
            "Classification":
                "Project fleet assumptions",
        },
        {
            "Input":
                "Base market demand",
            "Classification":
                "Modeled commercial assumption",
        },
        {
            "Input":
                "Fare multiplier",
            "Classification":
                "Modeled commercial assumption",
        },
        {
            "Input":
                "Competition level",
            "Classification":
                "Modeled commercial assumption",
        },
        {
            "Input":
                "Seasonality",
            "Classification":
                "Modeled commercial assumption",
        },
        {
            "Input":
                "Operating costs",
            "Classification":
                "Modeled planning assumption",
        },
        {
            "Input":
                "Route selection",
            "Classification":
                "Optimization output",
        },
    ]
)

st.dataframe(
    classification,
    use_container_width=True,
    hide_index=True,
)


# --------------------------------------------------
# Scope and limitations
# --------------------------------------------------

st.subheader(
    "Scope & Limitations"
)

st.write(
    """
    Aerofrite is designed as a strategic network-planning
    model rather than a complete airline scheduling or
    revenue-management system.
    """
)

st.markdown(
    """
    The current model does **not** explicitly represent:

    - individual aircraft tail assignment
    - crew scheduling and legal duty limits
    - airport slot constraints
    - exact departure and arrival times
    - detailed maintenance scheduling
    - connecting passenger flows
    - day-of-week demand variation
    - aircraft recovery after disruptions
    - live competitor schedules or capacity
    - dynamic ticket pricing
    - booking curves
    - spill and recapture between routes
    - airport curfews
    - empirically calibrated demand forecasting
    """
)

st.write(
    """
    These simplifications are intentional. The project's
    focus is strategic route selection, frequency choice,
    fleet-capacity allocation, and scenario analysis.
    """
)


# --------------------------------------------------
# Technology
# --------------------------------------------------

st.subheader(
    "Technology"
)

technology = pd.DataFrame(
    [
        {
            "Component":
                "Data processing",
            "Technology":
                "Python / pandas",
        },
        {
            "Component":
                "Optimization",
            "Technology":
                "Google OR-Tools CP-SAT",
        },
        {
            "Component":
                "Web application",
            "Technology":
                "Streamlit",
        },
        {
            "Component":
                "Network mapping",
            "Technology":
                "PyDeck",
        },
        {
            "Component":
                "Testing",
            "Technology":
                "pytest",
        },
        {
            "Component":
                "Version control",
            "Technology":
                "Git / GitHub",
        },
    ]
)

st.dataframe(
    technology,
    use_container_width=True,
    hide_index=True,
)


# --------------------------------------------------
# Final note
# --------------------------------------------------

st.divider()

st.caption(
    """
    Aerofrite was built as a portfolio project exploring
    airline network design, operations research, route
    economics, and interactive decision-support tooling.
    """
)