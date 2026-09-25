import pandas as pd

from src.economics import (
    calculate_route_economics,
)


def test_passengers_cannot_exceed_capacity():

    route = pd.Series(
        {
            "route_id": "TEST",
            "weekly_demand": 5000,
            "average_fare": 100,
            "variable_cost_per_rotation": 5000,
            "weekly_fixed_route_cost": 10000,
            "round_trip_block_hours": 5,
        }
    )

    result = calculate_route_economics(
        route=route,
        frequency=3,
        seats=180,
    )

    assert result["weekly_seats"] == 1080
    assert result["passengers"] == 1080