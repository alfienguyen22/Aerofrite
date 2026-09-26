import pandas as pd
import streamlit as st

from src.app_state import (
    get_planning_state,
)
from src.app_services import (
    build_route_details,
    get_optimized_network,
)
from src.demand import (
    build_frequency_curve,
    calculate_effective_demand,
)
from src.market_adjustments import (
    COMPETITION_MULTIPLIERS,
    SEASONALITY_MULTIPLIERS,
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
# Header
# --------------------------------------------------

st.title(
    "📈 Demand & Market Model"
)

st.write(
    """
    Explore the assumptions that translate underlying
    market demand into Aerofrite's modeled effective
    passenger demand.
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
# Model flow
# --------------------------------------------------

st.info(
    """
    Base Market Demand → Seasonality → Competition →
    Frequency Response → Effective Demand →
    Seat Capacity → Passengers Carried
    """
)


# --------------------------------------------------
# Demand-model navigation
# --------------------------------------------------

demand_view = st.radio(
    "Demand analysis view",
    options=[
        "Frequency Response",
        "Market Adjustments",
        "Current Network",
    ],
    horizontal=True,
    label_visibility="collapsed",
    key="demand_analysis_view",
)


# ==================================================
# FREQUENCY RESPONSE
# ==================================================

if demand_view == "Frequency Response":

    st.subheader(
        "Frequency-Sensitive Demand"
    )

    st.write(
        """
        Aerofrite assumes passengers value service
        frequency differently by market type.
        Business markets are modeled as more sensitive
        to low frequency than leisure markets, with
        mixed markets between the two.
        """
    )

    # ----------------------------------------------
    # Frequency-response curve
    # ----------------------------------------------

    frequency_curve = pd.DataFrame(
        build_frequency_curve()
    )

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
        Seven weekly round trips represent the baseline
        frequency-response level of 100%. Values above
        100% represent additional modeled demand response
        from higher service frequency.
        """
    )

    # ----------------------------------------------
    # Interactive market explorer
    # ----------------------------------------------

    st.markdown(
        "**Explore a Hypothetical Market**"
    )

    explorer_col1, explorer_col2 = (
        st.columns(2)
    )

    with explorer_col1:

        explorer_market_type = (
            st.selectbox(
                "Market type",
                options=[
                    "business",
                    "mixed",
                    "leisure",
                ],
                index=1,
                format_func=(
                    lambda value:
                    value.title()
                ),
                key=(
                    "demand_market_type"
                ),
            )
        )

    with explorer_col2:

        explorer_base_demand = (
            st.slider(
                "Base weekly demand",
                min_value=500,
                max_value=5000,
                value=2000,
                step=100,
                key=(
                    "demand_base_demand"
                ),
            )
        )

    explorer_frequencies = [
        0,
        3,
        4,
        7,
        10,
        14,
    ]

    explorer_rows = []

    for frequency in (
        explorer_frequencies
    ):

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

                "Frequency Response (%)":
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
        (
            f"**Effective Demand — "
            f"{explorer_market_type.title()} "
            f"Market**"
        )
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

    # ----------------------------------------------
    # Key frequency examples
    # ----------------------------------------------

    freq_3 = calculate_effective_demand(
        base_weekly_demand=(
            explorer_base_demand
        ),
        market_type=(
            explorer_market_type
        ),
        frequency=3,
    )

    freq_7 = calculate_effective_demand(
        base_weekly_demand=(
            explorer_base_demand
        ),
        market_type=(
            explorer_market_type
        ),
        frequency=7,
    )

    freq_14 = calculate_effective_demand(
        base_weekly_demand=(
            explorer_base_demand
        ),
        market_type=(
            explorer_market_type
        ),
        frequency=14,
    )

    demand_metric1, demand_metric2, (
        demand_metric3
    ) = st.columns(3)

    demand_metric1.metric(
        "3x Weekly",
        f"{freq_3:,}",
    )

    demand_metric2.metric(
        "Daily",
        f"{freq_7:,}",
    )

    demand_metric3.metric(
        "2x Daily",
        f"{freq_14:,}",
    )

    # ----------------------------------------------
    # Assumption table
    # ----------------------------------------------

    with st.expander(
        "View frequency-response assumptions"
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
        Frequency-response factors are transparent
        Aerofrite modeling assumptions and are not
        empirically calibrated forecasts of observed
        passenger behavior.
        """
    )


# ==================================================
# MARKET ADJUSTMENTS
# ==================================================

elif demand_view == "Market Adjustments":

    st.subheader(
        "Competition & Seasonality"
    )

    st.write(
        """
        Before frequency response is applied, Aerofrite
        adjusts underlying market demand for seasonality
        and modeled competitive intensity.
        """
    )

    # ----------------------------------------------
    # Competition assumptions
    # ----------------------------------------------

    st.markdown(
        "**Competition Adjustment**"
    )

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

    competition_col1, competition_col2 = (
        st.columns(
            [
                1,
                2,
            ]
        )
    )

    with competition_col1:

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

    with competition_col2:

        st.write(
            """
            Higher modeled competitive intensity reduces
            the share of underlying market demand assumed
            to be addressable by Aerofrite.

            Competition categories are scenario inputs,
            not measured market-share estimates or live
            competitor schedules.
            """
        )

    # ----------------------------------------------
    # Seasonality assumptions
    # ----------------------------------------------

    st.markdown(
        "**Seasonality Adjustment**"
    )

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

    seasonality_table = pd.DataFrame(
        seasonality_rows
    )

    seasonality_pivot = (
        seasonality_table.pivot(
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
        in seasonality_pivot.columns
    ]

    seasonality_pivot = (
        seasonality_pivot[
            [
                "Market Type",
                *season_columns,
            ]
        ]
    )

    st.dataframe(
        seasonality_pivot,
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

    st.markdown(
        "**How the adjustments combine**"
    )

    example_base_demand = 2000
    example_market_type = "leisure"
    example_competition = "medium"
    example_season = "summer"
    example_frequency = 4

    seasonal_factor = (
        SEASONALITY_MULTIPLIERS[
            example_market_type
        ][
            example_season
        ]
    )

    competition_factor = (
        COMPETITION_MULTIPLIERS[
            example_competition
        ]
    )

    adjusted_market_demand = round(
        example_base_demand
        * seasonal_factor
        * competition_factor
    )

    final_effective_demand = (
        calculate_effective_demand(
            base_weekly_demand=(
                adjusted_market_demand
            ),
            market_type=(
                example_market_type
            ),
            frequency=(
                example_frequency
            ),
        )
    )

    st.code(
        (
            "Illustrative leisure market\n\n"
            "Base demand                 2,000\n"
            "× Summer factor             1.25\n"
            "× Medium competition        0.90\n"
            "────────────────────────────────\n"
            f"Adjusted market demand     "
            f"{adjusted_market_demand:,}\n"
            "× 4x weekly response        0.75\n"
            "────────────────────────────────\n"
            f"Effective demand           "
            f"{final_effective_demand:,}"
        ),
        language=None,
    )

    st.caption(
        """
        Competition and seasonality multipliers are
        simplified scenario assumptions designed to
        make commercial tradeoffs explicit and
        interpretable.
        """
    )


# ==================================================
# CURRENT NETWORK
# ==================================================

else:

    st.subheader(
        "Demand Behavior in Current Network"
    )

    st.write(
        """
        See how the current optimized network combines
        base demand, seasonality, competition, and
        frequency response across selected routes.
        """
    )

    result = get_optimized_network(
        fleet_size=fleet_size,
        season=season,
        operational_buffer=(
            operational_buffer
        ),
    )

    route_details = (
        build_route_details(
            result["routes"],
            active_only=True,
        )
    )

    if route_details.empty:

        st.info(
            """
            No active routes are available under the
            current planning assumptions.
            """
        )

    else:

        network_demand = (
            route_details.copy()
        )

        # ------------------------------------------
        # Demand-chain percentages
        # ------------------------------------------

        network_demand[
            "frequency_response_percent"
        ] = (
            network_demand[
                "demand_multiplier"
            ]
            * 100
        )

        network_demand[
            "effective_vs_base_percent"
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
            "load_factor_percent"
        ] = (
            network_demand[
                "load_factor"
            ]
            * 100
        )

        # ------------------------------------------
        # Summary by market type
        # ------------------------------------------

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

                base_demand=(
                    "weekly_demand",
                    "sum",
                ),

                adjusted_demand=(
                    "adjusted_market_demand",
                    "sum",
                ),

                effective_demand=(
                    "effective_demand",
                    "sum",
                ),

                passengers=(
                    "passengers",
                    "sum",
                ),
            )
            .reset_index()
        )

        market_summary[
            "effective_vs_base_percent"
        ] = (
            market_summary[
                "effective_demand"
            ]
            / market_summary[
                "base_demand"
            ]
            * 100
        )

        market_summary = (
            market_summary.rename(
                columns={
                    "market_type":
                        "Market Type",

                    "routes":
                        "Routes",

                    "average_frequency":
                        "Average Frequency",

                    "base_demand":
                        "Base Demand",

                    "adjusted_demand":
                        "Adjusted Demand",

                    "effective_demand":
                        "Effective Demand",

                    "passengers":
                        "Passengers",

                    "effective_vs_base_percent":
                        "Effective vs Base (%)",
                }
            )
        )

        market_summary[
            "Market Type"
        ] = (
            market_summary[
                "Market Type"
            ]
            .str.title()
        )

        st.markdown(
            "**Current Network by Market Type**"
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

                "Base Demand":
                    st.column_config.NumberColumn(
                        format="%d",
                    ),

                "Adjusted Demand":
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

                "Effective vs Base (%)":
                    st.column_config.NumberColumn(
                        format="%.1f%%",
                    ),
            },
        )

        # ------------------------------------------
        # Route-level details
        # ------------------------------------------

        route_demand_display = (
            network_demand[
                [
                    "route_id",
                    "market_type",
                    "competition_level",
                    "frequency",
                    "weekly_demand",
                    "seasonality_multiplier",
                    "competition_multiplier",
                    "adjusted_market_demand",
                    "demand_multiplier",
                    "effective_demand",
                    "passengers",
                    "load_factor_percent",
                ]
            ]
            .copy()
        )

        route_demand_display = (
            route_demand_display.rename(
                columns={
                    "route_id":
                        "Route",

                    "market_type":
                        "Market Type",

                    "competition_level":
                        "Competition",

                    "frequency":
                        "Weekly Frequency",

                    "weekly_demand":
                        "Base Demand",

                    "seasonality_multiplier":
                        "Seasonal Factor",

                    "competition_multiplier":
                        "Competition Factor",

                    "adjusted_market_demand":
                        "Adjusted Demand",

                    "demand_multiplier":
                        "Frequency Response",

                    "effective_demand":
                        "Effective Demand",

                    "passengers":
                        "Passengers",

                    "load_factor_percent":
                        "Load Factor",
                }
            )
        )

        route_demand_display[
            "Market Type"
        ] = (
            route_demand_display[
                "Market Type"
            ]
            .str.title()
        )

        route_demand_display[
            "Competition"
        ] = (
            route_demand_display[
                "Competition"
            ]
            .str.title()
        )

        route_demand_display[
            "Seasonal Factor"
        ] = (
            route_demand_display[
                "Seasonal Factor"
            ]
            * 100
        )

        route_demand_display[
            "Competition Factor"
        ] = (
            route_demand_display[
                "Competition Factor"
            ]
            * 100
        )

        route_demand_display[
            "Frequency Response"
        ] = (
            route_demand_display[
                "Frequency Response"
            ]
            * 100
        )

        route_demand_display = (
            route_demand_display.sort_values(
                by=[
                    "Market Type",
                    "Route",
                ]
            )
        )

        with st.expander(
            "View route-level demand chain"
        ):

            st.dataframe(
                route_demand_display,
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

                    "Seasonal Factor":
                        st.column_config.NumberColumn(
                            format="%.0f%%",
                        ),

                    "Competition Factor":
                        st.column_config.NumberColumn(
                            format="%.0f%%",
                        ),

                    "Adjusted Demand":
                        st.column_config.NumberColumn(
                            format="%d",
                        ),

                    "Frequency Response":
                        st.column_config.NumberColumn(
                            format="%.0f%%",
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
                },
            )

        st.caption(
            """
            Market-type summaries describe the current
            optimized network. They should not be
            interpreted as isolated causal effects of
            market type because route economics and fleet
            constraints also influence network selection.
            """
        )


# --------------------------------------------------
# Global methodology note
# --------------------------------------------------

st.divider()

st.caption(
    """
    Aerofrite's demand model is intentionally transparent.
    Frequency response, seasonality, competition, and base
    market demand are scenario assumptions rather than
    calibrated forecasts of real airline passenger demand.
    """
)