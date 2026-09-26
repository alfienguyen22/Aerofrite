import streamlit as st

from src.app_services import (
    get_case_study,
)


# --------------------------------------------------
# Load fixed case study
# --------------------------------------------------

case_study = get_case_study()

seasonal_summary = (
    case_study[
        "seasonal_summary"
    ].copy()
)

seasonal_impact = (
    case_study[
        "seasonal_impact"
    ]
)

resilience_summary = (
    case_study[
        "resilience_summary"
    ].copy()
)

resilience_impact = (
    case_study[
        "resilience_impact"
    ]
)

network_changes = (
    case_study[
        "winter_to_summer"
    ].copy()
)


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title(
    "📋 Network Planning Case Study"
)

st.write(
    """
    How should a Brussels-based airline deploy a
    five-aircraft Airbus A320neo fleet across changing
    seasonal demand while preserving operational
    flexibility?
    """
)

st.info(
    """
    This is a fixed benchmark case study:
    5 Airbus A320neo aircraft • Brussels hub •
    10% operational reserve.

    Sidebar planning controls do not change this page.
    """
)


# --------------------------------------------------
# Case-study assumptions
# --------------------------------------------------

st.subheader(
    "Planning Problem"
)

st.write(
    """
    Aerofrite must decide which candidate destinations
    to serve and how frequently to operate them while
    allocating a limited pool of aircraft hours.

    The optimizer maximizes modeled weekly network
    contribution while accounting for route economics,
    frequency-sensitive demand, competition,
    seasonality, and fleet capacity.
    """
)

assumption_col1, assumption_col2, (
    assumption_col3
), assumption_col4 = st.columns(4)

assumption_col1.metric(
    "Fleet",
    "5 aircraft",
)

assumption_col2.metric(
    "Aircraft",
    "A320neo",
)

assumption_col3.metric(
    "Operational Reserve",
    "10%",
)

assumption_col4.metric(
    "Planning Capacity",
    "346.5 h",
)


# --------------------------------------------------
# Headline seasonal result
# --------------------------------------------------

st.subheader(
    "Seasonal Network Strategy"
)

winter_row = (
    seasonal_summary[
        seasonal_summary[
            "Season"
        ] == "Winter"
    ]
    .iloc[0]
)

summer_row = (
    seasonal_summary[
        seasonal_summary[
            "Season"
        ] == "Summer"
    ]
    .iloc[0]
)


passenger_growth_percent = (
    seasonal_impact[
        "passenger_change"
    ]
    / winter_row[
        "Passengers"
    ]
    * 100
)

contribution_growth_percent = (
    seasonal_impact[
        "contribution_change"
    ]
    / winter_row[
        "Contribution (€)"
    ]
    * 100
)


headline1, headline2, headline3, (
    headline4
) = st.columns(4)

headline1.metric(
    "Winter Passengers",
    (
        f"{int(winter_row['Passengers']):,}"
    ),
)

headline2.metric(
    "Summer Passengers",
    (
        f"{int(summer_row['Passengers']):,}"
    ),
    delta=(
        f"+"
        f"{seasonal_impact['passenger_change']:,} "
        f"({passenger_growth_percent:.1f}%)"
    ),
)

headline3.metric(
    "Summer Contribution",
    (
        f"€"
        f"{summer_row['Contribution (€)']:,.0f}"
    ),
    delta=(
        f"+€"
        f"{seasonal_impact['contribution_change']:,.0f}"
    ),
)

headline4.metric(
    "Destinations",
    (
        f"{int(winter_row['Destinations'])}"
        f" → "
        f"{int(summer_row['Destinations'])}"
    ),
    delta=(
        f"+"
        f"{seasonal_impact['destination_change']}"
    ),
)


st.success(
    (
        f"With fleet size and reserve held constant, "
        f"the modeled summer network carries "
        f"{passenger_growth_percent:.1f}% more passengers "
        f"and produces "
        f"{contribution_growth_percent:.1f}% more weekly "
        f"contribution than the winter network."
    )
)


# --------------------------------------------------
# Seasonal results
# --------------------------------------------------

st.markdown(
    "**Seasonal Planning Results**"
)

st.dataframe(
    seasonal_summary,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Season":
            st.column_config.TextColumn(
                "Season"
            ),

        "Destinations":
            st.column_config.NumberColumn(
                format="%d",
            ),

        "Passengers":
            st.column_config.NumberColumn(
                format="%d",
            ),

        "Revenue (€)":
            st.column_config.NumberColumn(
                format="localized",
            ),

        "Cost (€)":
            st.column_config.NumberColumn(
                format="localized",
            ),

        "Contribution (€)":
            st.column_config.NumberColumn(
                format="localized",
            ),

        "Scheduled Hours":
            st.column_config.NumberColumn(
                format="%.1f",
            ),

        "Planning Capacity":
            st.column_config.NumberColumn(
                format="%.1f",
            ),

        "Planning Utilization (%)":
            st.column_config.NumberColumn(
                format="%.1f%%",
            ),
    },
)


# --------------------------------------------------
# Seasonal charts
# --------------------------------------------------

chart_col1, chart_col2 = (
    st.columns(2)
)

with chart_col1:

    st.markdown(
        "**Passengers by Season**"
    )

    passenger_chart = (
        seasonal_summary[
            [
                "Season",
                "Passengers",
            ]
        ]
        .set_index(
            "Season"
        )
    )

    st.bar_chart(
        passenger_chart
    )


with chart_col2:

    st.markdown(
        "**Contribution by Season**"
    )

    contribution_chart = (
        seasonal_summary[
            [
                "Season",
                "Contribution (€)",
            ]
        ]
        .set_index(
            "Season"
        )
    )

    st.bar_chart(
        contribution_chart
    )


# --------------------------------------------------
# Network reallocation
# --------------------------------------------------

st.subheader(
    "Winter → Summer Reallocation"
)

st.write(
    """
    The summer result is not simply the winter network
    with more passengers. The optimizer reallocates
    scarce aircraft hours between markets as modeled
    seasonal demand changes.
    """
)


added_routes = (
    network_changes[
        network_changes[
            "Change Type"
        ] == "Route added"
    ][
        "Route"
    ]
    .tolist()
)

removed_routes = (
    network_changes[
        network_changes[
            "Change Type"
        ] == "Route removed"
    ][
        "Route"
    ]
    .tolist()
)


change_col1, change_col2 = (
    st.columns(2)
)

with change_col1:

    st.markdown(
        "**Routes entering the summer network**"
    )

    if added_routes:

        st.write(
            " • ".join(
                added_routes
            )
        )

    else:

        st.write(
            "No routes added."
        )


with change_col2:

    st.markdown(
        "**Routes leaving the winter network**"
    )

    if removed_routes:

        st.write(
            " • ".join(
                removed_routes
            )
        )

    else:

        st.write(
            "No routes removed."
        )


with st.expander(
    "View all Winter → Summer frequency changes"
):

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
                    "Winter",
                    format="%d",
                ),

            "Frequency B":
                st.column_config.NumberColumn(
                    "Summer",
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


st.caption(
    """
    Under Aerofrite's modeled seasonal assumptions,
    summer shifts scarce capacity toward a broader set
    of leisure-oriented markets. These are optimization
    results, not forecasts of real airline route decisions.
    """
)


# --------------------------------------------------
# Operational resilience
# --------------------------------------------------

st.subheader(
    "Operational Resilience Tradeoff"
)

st.write(
    """
    The case study also compares the shoulder-season
    network with and without a 10% operational reserve.
    """
)


st.dataframe(
    resilience_summary,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Scenario":
            st.column_config.TextColumn(),

        "Destinations":
            st.column_config.NumberColumn(
                format="%d",
            ),

        "Passengers":
            st.column_config.NumberColumn(
                format="%d",
            ),

        "Contribution (€)":
            st.column_config.NumberColumn(
                format="localized",
            ),

        "Planning Capacity":
            st.column_config.NumberColumn(
                format="%.1f",
            ),

        "Scheduled Hours":
            st.column_config.NumberColumn(
                format="%.1f",
            ),
    },
)


no_reserve_contribution = (
    resilience_summary.iloc[0][
        "Contribution (€)"
    ]
)

reserve_cost_percent = (
    abs(
        resilience_impact[
            "contribution_change"
        ]
    )
    / no_reserve_contribution
    * 100
)


resilience1, resilience2, (
    resilience3
), resilience4 = st.columns(4)

resilience1.metric(
    "Capacity Reserved",
    (
        f"{resilience_impact['reserved_hours']:.1f} h"
    ),
)

resilience2.metric(
    "Passenger Change",
    (
        f"{resilience_impact['passenger_change']:+,}"
    ),
)

resilience3.metric(
    "Contribution Change",
    (
        f"-€"
        f"{abs(resilience_impact['contribution_change']):,.0f}"
    ),
)

resilience4.metric(
    "Modeled Contribution Cost",
    (
        f"{reserve_cost_percent:.1f}%"
    ),
)


st.info(
    (
        f"Reserving "
        f"{resilience_impact['reserved_hours']:.1f} "
        f"aircraft-hours reduces modeled shoulder-season "
        f"weekly contribution by approximately "
        f"€"
        f"{abs(resilience_impact['contribution_change']):,.0f} "
        f"({reserve_cost_percent:.1f}%) compared with "
        f"scheduling the full theoretical fleet capacity."
    )
)


# --------------------------------------------------
# Planning interpretation
# --------------------------------------------------

st.subheader(
    "Planning Interpretation"
)

st.markdown(
    """
    **Aircraft capacity has an opportunity cost.**  
    A route can generate positive standalone contribution
    and still remain closed if another use of the aircraft
    produces greater network contribution.

    **Seasonal planning requires network re-optimization.**  
    Changing demand does more than alter passenger totals.
    It can change which destinations are served and the
    frequencies assigned to them.

    **Utilization alone does not determine network quality.**  
    Winter, shoulder, and summer all use almost all available
    planning capacity, yet generate materially different
    commercial outcomes.

    **Operational resilience has a measurable tradeoff.**  
    Reserving fleet capacity reduces scheduled flying but
    provides additional operational flexibility.
    """
)


# --------------------------------------------------
# Scope and limitations
# --------------------------------------------------

with st.expander(
    "Case-study scope and limitations"
):

    st.write(
        """
        Aerofrite is a strategic network-planning model,
        not a complete airline scheduling system.

        The current model does not explicitly include
        individual aircraft tail assignments, crew
        scheduling, airport slot constraints, detailed
        maintenance events, connecting passengers,
        departure times, day-of-week demand, aircraft
        recovery operations, live competitor schedules,
        or empirically calibrated demand forecasts.

        Commercial assumptions should therefore be
        interpreted as transparent scenario inputs rather
        than predictions of actual airline performance.
        """
    )


# --------------------------------------------------
# Conclusion
# --------------------------------------------------

st.subheader(
    "Case Study Conclusion"
)

st.write(
    """
    The case study demonstrates how mathematical
    optimization can combine commercial demand assumptions
    with limited aircraft capacity to support strategic
    airline network-planning decisions.

    Under the modeled assumptions, seasonal demand changes
    produce a substantial reallocation of Aerofrite's
    Brussels network, while the operational-reserve
    analysis makes the commercial cost of resilience
    explicit.
    """
)


st.divider()

st.caption(
    """
    The complete written case study is available in
    CASE_STUDY.md in the Aerofrite repository.
    """
)