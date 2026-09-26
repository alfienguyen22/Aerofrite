import pandas as pd
from src.demand import (
    calculate_effective_demand,
    get_frequency_multiplier,
)

from src.market_adjustments import (
    calculate_adjusted_market_demand,
    get_competition_multiplier,
    get_seasonality_multiplier,
)


# File paths
ROUTES_PATH = "data/routes.csv"
AIRCRAFT_PATH = "data/aircraft.csv"


# Frequency-sensitive demand assumptions.
# THIS HAS BEEN MIGRATED TO DEMAND.PY
# =======================================================
# FREQUENCY_DEMAND_MULTIPLIERS = {
#     "business": {
#         0: 0.00,
#         3: 0.30,
#         4: 0.45,
#         7: 1.00,
#         10: 1.12,
#         14: 1.25,
#     },
#     "mixed": {
#         0: 0.00,
#         3: 0.45,
#         4: 0.60,
#         7: 1.00,
#         10: 1.08,
#         14: 1.15,
#     },
#     "leisure": {
#         0: 0.00,
#         3: 0.60,
#         4: 0.75,
#         7: 1.00,
#         10: 1.04,
#         14: 1.08,
#     },
# }


def calculate_route_economics(
    route,
    frequency,
    seats,
    season="shoulder",
):
    """
    Calculate the weekly economics of one route
    at a given round-trip frequency.

    Parameters
    ----------
    route : pandas Series
        One row from routes.csv.

    frequency : int
        Number of weekly round trips.

    seats : int
        Seats per aircraft.

    Returns
    -------
    dict
        Route economics for the selected frequency.
    """

    market_type = route["market_type"]

    # Older synthetic test routes may not include
    # competition_level. Treat those as low competition
    # so existing unit tests remain backwards-compatible.
    competition_level = route.get(
        "competition_level",
        "low",
    )

    seasonality_multiplier = (
        get_seasonality_multiplier(
            market_type=market_type,
            season=season,
        )
    )

    competition_multiplier = (
        get_competition_multiplier(
            competition_level=competition_level,
        )
    )

    adjusted_market_demand = (
        calculate_adjusted_market_demand(
            base_weekly_demand=route[
                "weekly_demand"
            ],
            market_type=market_type,
            competition_level=competition_level,
            season=season,
        )
    )

    demand_multiplier = (
        get_frequency_multiplier(
            market_type=market_type,
            frequency=frequency,
        )
    )

    # If the route is closed, all economics are zero.
    if frequency == 0:
        return {
            "route_id": route["route_id"],
            "frequency": 0,
            "market_type": market_type,
            "weekly_seats": 0,
            "passengers": 0,
            "load_factor": 0.0,
            "demand_multiplier": 0.0,
            "effective_demand": 0,
            "season": season,
            "seasonality_multiplier": (
                seasonality_multiplier
            ),
            "competition_level": (
                competition_level
            ),
            "competition_multiplier": (
                competition_multiplier
            ),
            "adjusted_market_demand": (
                adjusted_market_demand
            ),
            "revenue": 0.0,
            "variable_cost": 0.0,
            "fixed_route_cost": 0.0,
            "total_cost": 0.0,
            "contribution": 0.0,
            "aircraft_hours": 0.0,
            "contribution_per_aircraft_hour": 0.0,
        }

    # Demand Aerofrite can capture at this frequency.
    effective_demand = (
        calculate_effective_demand(
            base_weekly_demand=(
                adjusted_market_demand
            ),
            market_type=market_type,
            frequency=frequency,
        )
    )

    # Weekly capacity across both directions.
    weekly_seats = (
        frequency
        * seats
        * 2
    )

    # Passengers cannot exceed demand or capacity.
    passengers = min(
        effective_demand,
        weekly_seats,
    )

    # Load factor.
    load_factor = (
        passengers
        / weekly_seats
    )

    # Revenue.
    revenue = (
        passengers
        * route["average_fare"]
    )

    # Variable operating cost.
    variable_cost = (
        frequency
        * route["variable_cost_per_rotation"]
    )

    # Fixed weekly route cost.
    fixed_route_cost = (
        route["weekly_fixed_route_cost"]
    )

    # Total cost.
    total_cost = (
        variable_cost
        + fixed_route_cost
    )

    # Weekly contribution.
    contribution = (
        revenue
        - total_cost
    )

    # Aircraft time consumed.
    aircraft_hours = (
        frequency
        * route["round_trip_block_hours"]
    )

    # Contribution generated per aircraft hour.
    contribution_per_aircraft_hour = (
        contribution / aircraft_hours
        if aircraft_hours > 0
        else 0
    )

    return {
        "route_id": route["route_id"],
        "frequency": frequency,
        "market_type": market_type,
        "weekly_seats": int(
            weekly_seats
        ),
        "passengers": int(
            passengers
        ),
        "load_factor": round(
            load_factor,
            4,
        ),
        "demand_multiplier": round(
            demand_multiplier,
            2,
        ),
        "effective_demand": int(
            effective_demand
        ),
        "season": season,
        "seasonality_multiplier": (
            seasonality_multiplier
        ),
        "competition_level": (
            competition_level
        ),
        "competition_multiplier": (
            competition_multiplier
        ),
        "adjusted_market_demand": (
            adjusted_market_demand
        ),
        "revenue": round(
            revenue,
            2,
        ),
        "variable_cost": round(
            variable_cost,
            2,
        ),
        "fixed_route_cost": round(
            fixed_route_cost,
            2,
        ),
        "total_cost": round(
            total_cost,
            2,
        ),
        "contribution": round(
            contribution,
            2,
        ),
        "aircraft_hours": round(
            aircraft_hours,
            2,
        ),
        "contribution_per_aircraft_hour": round(
            contribution_per_aircraft_hour,
            2,
        ),

    }


def evaluate_route(
    destination,
    frequency,
):
    """
    Load Aerofrite data and evaluate one route.
    """

    routes = pd.read_csv(
        ROUTES_PATH
    )

    aircraft = pd.read_csv(
        AIRCRAFT_PATH
    )

    route_rows = routes[
        routes["destination"]
        == destination
    ]

    if len(route_rows) != 1:
        raise ValueError(
            f"Expected exactly one route for "
            f"{destination}, "
            f"found {len(route_rows)}"
        )

    route = route_rows.iloc[0]

    aircraft_row = aircraft.iloc[0]

    seats = int(
        aircraft_row["seats"]
    )

    allowed_frequencies = [
        int(value)
        for value in str(
            route["frequency_options"]
        ).split("|")
    ]

    if frequency not in allowed_frequencies:
        raise ValueError(
            f"Frequency {frequency} is not allowed "
            f"for {destination}. "
            f"Allowed frequencies: "
            f"{allowed_frequencies}"
        )

    return calculate_route_economics(
        route=route,
        frequency=frequency,
        seats=seats,
    )