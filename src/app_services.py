import pandas as pd
import streamlit as st
from src.case_study import build_case_study

from src.economics import calculate_route_economics
from src.optimizer import optimize_network
from src.scenarios import (
    analyze_reserve_breakpoints,
    compare_fleet_scenarios,
    compare_season_scenarios,
)


ROUTES_PATH = "data/routes.csv"
AIRPORTS_PATH = "data/airports.csv"
AIRCRAFT_PATH = "data/aircraft.csv"


# --------------------------------------------------
# Cached reference data
# --------------------------------------------------

@st.cache_data
def load_reference_data():
    """
    Load static Aerofrite reference datasets.

    These files do not normally change while the
    Streamlit app is running, so they are cached.
    """

    routes = pd.read_csv(
        ROUTES_PATH
    )

    airports = pd.read_csv(
        AIRPORTS_PATH
    )

    aircraft = pd.read_csv(
        AIRCRAFT_PATH
    )

    return {
        "routes": routes,
        "airports": airports,
        "aircraft": aircraft,
    }


# --------------------------------------------------
# Cached optimizer
# --------------------------------------------------

@st.cache_data(
    show_spinner=False
)
def get_optimized_network(
    fleet_size,
    season,
    operational_buffer,
):
    """
    Run and cache one optimized Aerofrite
    network scenario.
    """

    return optimize_network(
        fleet_size_override=fleet_size,
        season=season,
        operational_buffer=(
            operational_buffer
        ),
        save_output=False,
        print_results=False,
    )


# --------------------------------------------------
# Route-detail enrichment
# --------------------------------------------------

def build_route_details(
    result_routes,
    active_only=True,
):
    """
    Add route and airport reference information
    to optimizer output.
    """

    reference = load_reference_data()

    route_reference = reference[
        "routes"
    ]

    airport_reference = reference[
        "airports"
    ]

    routes = result_routes.copy()

    if active_only:

        routes = routes[
            routes["frequency"] > 0
        ].copy()

    routes = routes.merge(
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

    routes = routes.merge(
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

    routes = routes.rename(
        columns={
            "name": "airport_name",
        }
    )

    if not routes.empty:

        routes[
            "base_demand_capture"
        ] = (
            routes["passengers"]
            / routes["weekly_demand"]
        )

    return routes

# --------------------------------------------------
# Route frequency analysis
# --------------------------------------------------

@st.cache_data(
    show_spinner=False
)
def get_route_frequency_analysis(
    route_id,
    season,
):
    """
    Evaluate every allowed frequency for one
    candidate route.

    This is a standalone route analysis and does
    not account for network opportunity cost.
    """

    reference = load_reference_data()

    route_reference = reference[
        "routes"
    ]

    aircraft_reference = reference[
        "aircraft"
    ]

    route_match = route_reference[
        route_reference["route_id"]
        == route_id
    ]

    if route_match.empty:

        raise ValueError(
            f"Unknown route: {route_id}"
        )

    route = route_match.iloc[0]

    seats = int(
        aircraft_reference.iloc[0][
            "seats"
        ]
    )

    frequencies = [
        int(value)
        for value in str(
            route[
                "frequency_options"
            ]
        ).split("|")
    ]

    rows = []

    for frequency in frequencies:

        economics = (
            calculate_route_economics(
                route=route,
                frequency=frequency,
                seats=seats,
                season=season,
            )
        )

        rows.append(
            economics
        )

    return pd.DataFrame(
        rows
    )


# --------------------------------------------------
# Closed-route analysis
# --------------------------------------------------

@st.cache_data(
    show_spinner=False
)
def get_closed_route_analysis(
    fleet_size,
    season,
    operational_buffer,
):
    """
    Analyze candidate routes that are closed in
    the current optimized network.
    """

    result = get_optimized_network(
        fleet_size=fleet_size,
        season=season,
        operational_buffer=(
            operational_buffer
        ),
    )

    reference = load_reference_data()

    route_reference = reference[
        "routes"
    ]

    airport_reference = reference[
        "airports"
    ]

    aircraft_reference = reference[
        "aircraft"
    ]

    seats = int(
        aircraft_reference.iloc[0][
            "seats"
        ]
    )

    closed_route_ids = set(
        result[
            "routes"
        ][
            result[
                "routes"
            ]["frequency"] == 0
        ][
            "route_id"
        ]
    )

    rows = []

    for _, route in (
        route_reference.iterrows()
    ):

        route_id = route[
            "route_id"
        ]

        if (
            route_id
            not in closed_route_ids
        ):
            continue

        frequencies = [
            int(value)
            for value in str(
                route[
                    "frequency_options"
                ]
            ).split("|")
            if int(value) > 0
        ]

        route_options = []

        for frequency in frequencies:

            economics = (
                calculate_route_economics(
                    route=route,
                    frequency=frequency,
                    seats=seats,
                    season=season,
                )
            )

            route_options.append(
                economics
            )

        best_option = max(
            route_options,
            key=lambda option:
                option[
                    "contribution"
                ],
        )

        destination = route[
            "destination"
        ]

        airport_match = (
            airport_reference[
                airport_reference[
                    "iata"
                ]
                == destination
            ]
        )

        if airport_match.empty:

            city = destination

        else:

            city = (
                airport_match.iloc[0][
                    "city"
                ]
            )

        if fleet_size == 0:

            reason = (
                "No fleet capacity"
            )

        elif (
            best_option[
                "contribution"
            ]
            <= 0
        ):

            reason = (
                "Non-positive modeled "
                "contribution at all tested "
                "frequencies"
            )

        else:

            reason = (
                "Positive standalone "
                "contribution, but not selected "
                "in optimal fleet allocation"
            )

        rows.append(
            {
                "Route":
                    route_id,

                "Destination":
                    city,

                "Market Type":
                    route[
                        "market_type"
                    ].title(),

                "Best Frequency":
                    best_option[
                        "frequency"
                    ],

                "Best Contribution (€)":
                    best_option[
                        "contribution"
                    ],

                "Contribution / Hour (€)":
                    best_option[
                        "contribution_per_aircraft_hour"
                    ],

                "Aircraft Hours Required":
                    best_option[
                        "aircraft_hours"
                    ],

                "Load Factor":
                    (
                        best_option[
                            "load_factor"
                        ]
                        * 100
                    ),

                "Reason":
                    reason,
            }
        )

    return pd.DataFrame(
        rows
    )

# --------------------------------------------------
# Cached fleet-scenario analysis
# --------------------------------------------------

@st.cache_data(
    show_spinner=False
)
def get_fleet_scenario_analysis(
    fleet_sizes,
    season,
    operational_buffer,
):
    """
    Compare multiple fleet-size scenarios while
    holding season and operational reserve constant.
    """

    return compare_fleet_scenarios(
        fleet_sizes=list(
            fleet_sizes
        ),
        season=season,
        operational_buffer=(
            operational_buffer
        ),
    )


# --------------------------------------------------
# Cached seasonal-scenario analysis
# --------------------------------------------------

@st.cache_data(
    show_spinner=False
)
def get_season_scenario_analysis(
    fleet_size,
    operational_buffer,
):
    """
    Compare winter, shoulder, and summer while
    holding fleet size and reserve constant.
    """

    return compare_season_scenarios(
        fleet_size=fleet_size,
        operational_buffer=(
            operational_buffer
        ),
    )


# --------------------------------------------------
# Cached reserve-breakpoint analysis
# --------------------------------------------------

@st.cache_data(
    show_spinner=False
)
def get_reserve_breakpoint_analysis(
    fleet_size,
    season,
    min_buffer_percent=0,
    max_buffer_percent=25,
    step_percent=1,
):
    """
    Find reserve levels where the optimized
    network changes.
    """

    return analyze_reserve_breakpoints(
        fleet_size=fleet_size,
        season=season,
        min_buffer_percent=(
            min_buffer_percent
        ),
        max_buffer_percent=(
            max_buffer_percent
        ),
        step_percent=(
            step_percent
        ),
    )

# --------------------------------------------------
# Cached case study
# --------------------------------------------------

@st.cache_data(
    show_spinner=False
)
def get_case_study():
    """
    Build and cache Aerofrite's fixed portfolio
    case-study scenario.
    """

    return build_case_study()