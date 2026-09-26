import pandas as pd
import streamlit as st

from src.optimizer import optimize_network


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