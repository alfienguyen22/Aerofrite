import pandas as pd
import streamlit as st

from src.app_state import (
    get_planning_state,
)
from src.app_services import (
    get_fleet_scenario_analysis,
    get_optimized_network,
    get_reserve_breakpoint_analysis,
    get_season_scenario_analysis,
)
from src.scenarios import (
    compare_networks,
)


# --------------------------------------------------
# Helper formatting
# --------------------------------------------------

def format_euro_delta(
    value,
):
    """
    Format a positive, negative, or zero
    euro change.
    """

    if value > 0:

        return (
            f"+€{value:,.0f}"
        )

    if value < 0:

        return (
            f"-€{abs(value):,.0f}"
        )

    return "€0"


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
# Header
# --------------------------------------------------

st.title(
    "📊 Scenario Analysis"
)

st.write(
    """
    Test how alternative fleet sizes, seasonal demand,
    and operational-reserve assumptions reshape
    Aerofrite's optimized network.
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
# Analysis navigation
# --------------------------------------------------

analysis_view = st.radio(
    "Scenario analysis view",
    options=[
        "Fleet Capacity",
        "Seasonality",
        "Operational Resilience",
    ],
    horizontal=True,
    label_visibility="collapsed",
    key="scenario_analysis_view",
)


# ==================================================
# FLEET CAPACITY
# ==================================================

if analysis_view == "Fleet Capacity":

    st.subheader(
        "Fleet Capacity"
    )

    st.write(
        """
        Compare nearby fleet sizes while holding the
        current season and operational-reserve
        assumptions constant.
        """
    )

    # ----------------------------------------------
    # Build nearby fleet scenarios
    # ----------------------------------------------

    scenario_fleet_sizes = sorted(
        set(
            [
                max(
                    0,
                    fleet_size - 1,
                ),
                fleet_size,
                min(
                    10,
                    fleet_size + 1,
                ),
            ]
        )
    )

    with st.spinner(
        "Evaluating fleet scenarios..."
    ):

        (
            scenario_summary,
            scenario_results,
        ) = get_fleet_scenario_analysis(
            fleet_sizes=tuple(
                scenario_fleet_sizes
            ),
            season=season,
            operational_buffer=(
                operational_buffer
            ),
        )

    # ----------------------------------------------
    # Summary
    # ----------------------------------------------

    st.markdown(
        "**Fleet Scenario Summary**"
    )

    fleet_display = (
        scenario_summary[
            [
                "Fleet Size",
                "Destinations",
                "Passengers",
                "Contribution (€)",
                "Aircraft Hours",
                "Available Hours",
                "Utilization",
                "Incremental Contribution (€)",
                "Incremental Contribution / Hour (€)",
            ]
        ]
        .copy()
    )

    st.dataframe(
        fleet_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Fleet Size":
                st.column_config.NumberColumn(
                    format="%d",
                ),

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

            "Aircraft Hours":
                st.column_config.NumberColumn(
                    format="%.1f",
                ),

            "Available Hours":
                st.column_config.NumberColumn(
                    format="%.1f",
                ),

            "Utilization":
                st.column_config.NumberColumn(
                    format="%.1f%%",
                ),

            "Incremental Contribution (€)":
                st.column_config.NumberColumn(
                    format="localized",
                ),

            "Incremental Contribution / Hour (€)":
                st.column_config.NumberColumn(
                    format="localized",
                ),
        },
    )

    # ----------------------------------------------
    # Charts
    # ----------------------------------------------

    chart_col1, chart_col2 = (
        st.columns(2)
    )

    with chart_col1:

        st.markdown(
            "**Modeled Weekly Contribution**"
        )

        contribution_chart = (
            scenario_summary[
                [
                    "Fleet Size",
                    "Contribution (€)",
                ]
            ]
            .set_index(
                "Fleet Size"
            )
        )

        st.bar_chart(
            contribution_chart
        )

    with chart_col2:

        st.markdown(
            "**Modeled Weekly Passengers**"
        )

        passenger_chart = (
            scenario_summary[
                [
                    "Fleet Size",
                    "Passengers",
                ]
            ]
            .set_index(
                "Fleet Size"
            )
        )

        st.bar_chart(
            passenger_chart
        )

    # ----------------------------------------------
    # Compare two fleet plans
    # ----------------------------------------------

    st.markdown(
        "**Compare Two Fleet Plans**"
    )

    current_index = (
        scenario_fleet_sizes.index(
            fleet_size
        )
    )

    if (
        current_index
        < len(
            scenario_fleet_sizes
        ) - 1
    ):

        alternative_index = (
            current_index + 1
        )

    elif current_index > 0:

        alternative_index = (
            current_index - 1
        )

    else:

        alternative_index = (
            current_index
        )

    compare_col1, compare_col2 = (
        st.columns(2)
    )

    with compare_col1:

        baseline_fleet = (
            st.selectbox(
                "Baseline fleet",
                options=(
                    scenario_fleet_sizes
                ),
                index=current_index,
                key=(
                    "fleet_compare_baseline"
                ),
            )
        )

    with compare_col2:

        alternative_fleet = (
            st.selectbox(
                "Alternative fleet",
                options=(
                    scenario_fleet_sizes
                ),
                index=(
                    alternative_index
                ),
                key=(
                    "fleet_compare_alternative"
                ),
            )
        )

    baseline_result = (
        scenario_results[
            baseline_fleet
        ]
    )

    alternative_result = (
        scenario_results[
            alternative_fleet
        ]
    )

    contribution_change = (
        alternative_result[
            "total_contribution"
        ]
        - baseline_result[
            "total_contribution"
        ]
    )

    passenger_change = (
        alternative_result[
            "total_passengers"
        ]
        - baseline_result[
            "total_passengers"
        ]
    )

    destination_change = (
        alternative_result[
            "destinations_served"
        ]
        - baseline_result[
            "destinations_served"
        ]
    )

    aircraft_hour_change = (
        alternative_result[
            "total_aircraft_hours"
        ]
        - baseline_result[
            "total_aircraft_hours"
        ]
    )

    st.markdown(
        (
            f"**Modeled Impact: "
            f"{baseline_fleet} → "
            f"{alternative_fleet} Aircraft**"
        )
    )

    impact1, impact2, impact3, (
        impact4
    ) = st.columns(4)

    impact1.metric(
        "Contribution Change",
        format_euro_delta(
            contribution_change
        ),
    )

    impact2.metric(
        "Passenger Change",
        (
            f"{passenger_change:+,.0f}"
        ),
    )

    impact3.metric(
        "Destination Change",
        (
            f"{destination_change:+,.0f}"
        ),
    )

    impact4.metric(
        "Aircraft Hours Change",
        (
            f"{aircraft_hour_change:+.1f}"
        ),
    )

    fleet_network_changes = (
        compare_networks(
            baseline_result,
            alternative_result,
        )
    )

    with st.expander(
        "View fleet network changes"
    ):

        if (
            fleet_network_changes.empty
        ):

            st.info(
                """
                The selected fleet scenarios produce
                the same route frequencies.
                """
            )

        else:

            st.dataframe(
                fleet_network_changes,
                use_container_width=True,
                hide_index=True,
            )

    st.caption(
        """
        Fleet-size comparisons hold season and
        operational reserve constant. Incremental
        contribution measures the modeled value of
        additional fleet capacity.
        """
    )


# ==================================================
# SEASONALITY
# ==================================================

elif analysis_view == "Seasonality":

    st.subheader(
        "Seasonal Network Comparison"
    )

    st.write(
        """
        Compare winter, shoulder, and summer while
        holding fleet size and operational reserve
        constant.
        """
    )

    with st.spinner(
        "Evaluating seasonal scenarios..."
    ):

        (
            season_summary,
            season_results,
        ) = get_season_scenario_analysis(
            fleet_size=fleet_size,
            operational_buffer=(
                operational_buffer
            ),
        )

    # ----------------------------------------------
    # Seasonal summary
    # ----------------------------------------------

    st.dataframe(
        season_summary,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Season":
                st.column_config.TextColumn(),

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

            "Aircraft Hours":
                st.column_config.NumberColumn(
                    format="%.1f",
                ),

            "Available Hours":
                st.column_config.NumberColumn(
                    format="%.1f",
                ),

            "Utilization":
                st.column_config.NumberColumn(
                    format="%.1f%%",
                ),
        },
    )

    # ----------------------------------------------
    # Compare two seasons
    # ----------------------------------------------

    st.markdown(
        "**Compare Two Seasons**"
    )

    season_options = [
        "winter",
        "shoulder",
        "summer",
    ]

    season_col1, season_col2 = (
        st.columns(2)
    )

    with season_col1:

        baseline_season = (
            st.selectbox(
                "Baseline season",
                options=season_options,
                index=0,
                format_func=(
                    lambda value:
                    value.title()
                ),
                key=(
                    "season_compare_baseline"
                ),
            )
        )

    with season_col2:

        alternative_season = (
            st.selectbox(
                "Alternative season",
                options=season_options,
                index=2,
                format_func=(
                    lambda value:
                    value.title()
                ),
                key=(
                    "season_compare_alternative"
                ),
            )
        )

    baseline_result = (
        season_results[
            baseline_season
        ]
    )

    alternative_result = (
        season_results[
            alternative_season
        ]
    )

    contribution_change = (
        alternative_result[
            "total_contribution"
        ]
        - baseline_result[
            "total_contribution"
        ]
    )

    passenger_change = (
        alternative_result[
            "total_passengers"
        ]
        - baseline_result[
            "total_passengers"
        ]
    )

    destination_change = (
        alternative_result[
            "destinations_served"
        ]
        - baseline_result[
            "destinations_served"
        ]
    )

    aircraft_hour_change = (
        alternative_result[
            "total_aircraft_hours"
        ]
        - baseline_result[
            "total_aircraft_hours"
        ]
    )

    st.markdown(
        (
            f"**Modeled Impact: "
            f"{baseline_season.title()} → "
            f"{alternative_season.title()}**"
        )
    )

    season_metric1, season_metric2, (
        season_metric3
    ), season_metric4 = st.columns(4)

    season_metric1.metric(
        "Contribution Change",
        format_euro_delta(
            contribution_change
        ),
    )

    season_metric2.metric(
        "Passenger Change",
        (
            f"{passenger_change:+,.0f}"
        ),
    )

    season_metric3.metric(
        "Destination Change",
        (
            f"{destination_change:+,.0f}"
        ),
    )

    season_metric4.metric(
        "Aircraft Hours Change",
        (
            f"{aircraft_hour_change:+.1f}"
        ),
    )

    seasonal_network_changes = (
        compare_networks(
            baseline_result,
            alternative_result,
        )
    )

    with st.expander(
        "View seasonal network changes"
    ):

        if (
            seasonal_network_changes.empty
        ):

            st.info(
                """
                The selected seasons produce the
                same route frequencies.
                """
            )

        else:

            st.dataframe(
                seasonal_network_changes,
                use_container_width=True,
                hide_index=True,
            )

    st.caption(
        """
        Seasonal comparisons keep fleet size and
        operational reserve constant, isolating the
        effect of Aerofrite's modeled seasonal-demand
        assumptions.
        """
    )


# ==================================================
# OPERATIONAL RESILIENCE
# ==================================================

else:

    st.subheader(
        "Operational Resilience"
    )

    st.write(
        """
        Examine the commercial tradeoff created by
        reserving part of theoretical fleet capacity
        for maintenance, disruption recovery, and
        operational flexibility.
        """
    )

    # ----------------------------------------------
    # Reserve scenarios
    # ----------------------------------------------

    reserve_percentages = sorted(
        set(
            [
                0,
                5,
                10,
                15,
                20,
                25,
                operational_buffer_percent,
            ]
        )
    )

    reserve_rows = []
    reserve_results = {}

    with st.spinner(
        "Evaluating reserve scenarios..."
    ):

        for reserve_percent in (
            reserve_percentages
        ):

            reserve_value = (
                reserve_percent
                / 100
            )

            reserve_result = (
                get_optimized_network(
                    fleet_size=(
                        fleet_size
                    ),
                    season=season,
                    operational_buffer=(
                        reserve_value
                    ),
                )
            )

            reserve_results[
                reserve_percent
            ] = reserve_result

            reserve_rows.append(
                {
                    "Operational Reserve (%)":
                        reserve_percent,

                    "Planning Capacity (h)":
                        reserve_result[
                            "available_aircraft_hours"
                        ],

                    "Scheduled Hours":
                        reserve_result[
                            "total_aircraft_hours"
                        ],

                    "Destinations":
                        reserve_result[
                            "destinations_served"
                        ],

                    "Passengers":
                        reserve_result[
                            "total_passengers"
                        ],

                    "Contribution (€)":
                        reserve_result[
                            "total_contribution"
                        ],
                }
            )

    reserve_analysis = pd.DataFrame(
        reserve_rows
    )

    # ----------------------------------------------
    # Reserve summary table
    # ----------------------------------------------

    st.markdown(
        "**Reserve Scenario Summary**"
    )

    st.dataframe(
        reserve_analysis,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Operational Reserve (%)":
                st.column_config.NumberColumn(
                    format="%d%%",
                ),

            "Planning Capacity (h)":
                st.column_config.NumberColumn(
                    format="%.1f",
                ),

            "Scheduled Hours":
                st.column_config.NumberColumn(
                    format="%.1f",
                ),

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
        },
    )

    # ----------------------------------------------
    # Contribution chart
    # ----------------------------------------------

    st.markdown(
        "**Modeled Contribution vs Operational Reserve**"
    )

    contribution_chart = (
        reserve_analysis[
            [
                "Operational Reserve (%)",
                "Contribution (€)",
            ]
        ]
        .set_index(
            "Operational Reserve (%)"
        )
    )

    st.line_chart(
        contribution_chart
    )

    # ----------------------------------------------
    # Current reserve vs no reserve
    # ----------------------------------------------

    no_reserve_result = (
        reserve_results[0]
    )

    current_result = (
        get_optimized_network(
            fleet_size=fleet_size,
            season=season,
            operational_buffer=(
                operational_buffer
            ),
        )
    )

    contribution_change = (
        current_result[
            "total_contribution"
        ]
        - no_reserve_result[
            "total_contribution"
        ]
    )

    passenger_change = (
        current_result[
            "total_passengers"
        ]
        - no_reserve_result[
            "total_passengers"
        ]
    )

    destination_change = (
        current_result[
            "destinations_served"
        ]
        - no_reserve_result[
            "destinations_served"
        ]
    )

    st.markdown(
        (
            f"**Current Reserve Impact: "
            f"0% → "
            f"{operational_buffer_percent}%**"
        )
    )

    reserve_metric1, reserve_metric2, (
        reserve_metric3
    ), reserve_metric4 = st.columns(4)

    reserve_metric1.metric(
        "Reserved Hours",
        (
            f"{current_result['reserved_aircraft_hours']:.1f} h"
        ),
    )

    reserve_metric2.metric(
        "Contribution Change",
        format_euro_delta(
            contribution_change
        ),
    )

    reserve_metric3.metric(
        "Passenger Change",
        (
            f"{passenger_change:+,.0f}"
        ),
    )

    reserve_metric4.metric(
        "Destination Change",
        (
            f"{destination_change:+,.0f}"
        ),
    )

    reserve_network_changes = (
        compare_networks(
            no_reserve_result,
            current_result,
        )
    )

    with st.expander(
        "View network changes caused by current reserve"
    ):

        if (
            reserve_network_changes.empty
        ):

            st.info(
                """
                The current reserve does not change
                route frequencies compared with the
                zero-reserve solution.
                """
            )

        else:

            st.dataframe(
                reserve_network_changes,
                use_container_width=True,
                hide_index=True,
            )

    # ----------------------------------------------
    # Capacity breakpoints
    # ----------------------------------------------

    st.markdown(
        "**Network Capacity Breakpoints**"
    )

    st.write(
        """
        A breakpoint occurs when reducing planning
        capacity forces at least one route frequency
        to change.
        """
    )

    with st.spinner(
        "Finding network breakpoints..."
    ):

        (
            reserve_breakpoints,
            _,
        ) = get_reserve_breakpoint_analysis(
            fleet_size=fleet_size,
            season=season,
            min_buffer_percent=0,
            max_buffer_percent=25,
            step_percent=1,
        )

    current_breakpoints = (
        reserve_breakpoints[
            reserve_breakpoints[
                "Reserve (%)"
            ]
            <= operational_buffer_percent
        ]
    )

    if not current_breakpoints.empty:

        current_regime = (
            current_breakpoints.iloc[
                -1
            ]
        )

        regime_start = int(
            current_regime[
                "Reserve (%)"
            ]
        )

        st.info(
            (
                f"At "
                f"{operational_buffer_percent}% "
                f"reserve, the current network "
                f"configuration first appears at "
                f"{regime_start}% reserve."
            )
        )

    future_breakpoints = (
        reserve_breakpoints[
            reserve_breakpoints[
                "Reserve (%)"
            ]
            > operational_buffer_percent
        ]
    )

    if not future_breakpoints.empty:

        next_breakpoint = int(
            future_breakpoints.iloc[
                0
            ][
                "Reserve (%)"
            ]
        )

        st.caption(
            (
                f"The next modeled network "
                f"change occurs at "
                f"{next_breakpoint}% reserve."
            )
        )

    else:

        st.caption(
            """
            No further network change occurs within
            the analyzed 0–25% reserve range.
            """
        )

    with st.expander(
        "View detailed network capacity breakpoints"
    ):

        st.dataframe(
            reserve_breakpoints,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Reserve (%)":
                    st.column_config.NumberColumn(
                        format="%d%%",
                    ),

                "Planning Capacity (h)":
                    st.column_config.NumberColumn(
                        format="%.1f",
                    ),

                "Scheduled Hours":
                    st.column_config.NumberColumn(
                        format="%.1f",
                    ),

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

                "Changed Routes":
                    st.column_config.NumberColumn(
                        format="%d",
                    ),
            },
        )

    st.caption(
        """
        Destination count does not necessarily decline
        at every higher reserve level. Because route
        frequencies are discrete, the optimizer may
        replace a higher-frequency service with multiple
        lower-frequency services while total planning
        capacity and modeled contribution decline.
        """
    )


# --------------------------------------------------
# Global model note
# --------------------------------------------------

st.divider()

st.caption(
    """
    Scenario results are outputs of Aerofrite's modeled
    assumptions rather than forecasts of actual airline
    performance. Comparisons isolate selected planning
    inputs while other modeled assumptions remain fixed.
    """
)