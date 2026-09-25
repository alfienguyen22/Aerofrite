import pandas as pd

from src.economics import (
    calculate_route_economics,
)


def test_passengers_cannot_exceed_capacity():

    route = pd.Series(
        {
            "route_id": "TEST",
            "market_type": "mixed",
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

    # 3 weekly round trips × 2 directions × 180 seats
    assert result["weekly_seats"] == 1080

    # Demand may be higher than capacity,
    # but passengers cannot exceed available seats.
    assert result["passengers"] == 1080


def test_closed_route_has_zero_economics():

    route = pd.Series(
        {
            "route_id": "TEST",
            "market_type": "mixed",
            "weekly_demand": 2000,
            "average_fare": 100,
            "variable_cost_per_rotation": 5000,
            "weekly_fixed_route_cost": 10000,
            "round_trip_block_hours": 5,
        }
    )

    result = calculate_route_economics(
        route=route,
        frequency=0,
        seats=180,
    )

    assert result["weekly_seats"] == 0
    assert result["passengers"] == 0
    assert result["effective_demand"] == 0
    assert result["revenue"] == 0
    assert result["variable_cost"] == 0
    assert result["fixed_route_cost"] == 0
    assert result["total_cost"] == 0
    assert result["contribution"] == 0
    assert result["aircraft_hours"] == 0


def test_lower_frequency_reduces_effective_demand():

    route = pd.Series(
        {
            "route_id": "TEST",
            "market_type": "mixed",
            "weekly_demand": 1000,
            "average_fare": 100,
            "variable_cost_per_rotation": 5000,
            "weekly_fixed_route_cost": 5000,
            "round_trip_block_hours": 5,
        }
    )

    three_weekly = calculate_route_economics(
        route=route,
        frequency=3,
        seats=180,
    )

    daily = calculate_route_economics(
        route=route,
        frequency=7,
        seats=180,
    )

    # Mixed-market multiplier:
    # 3/week = 45%
    # 7/week = 100%
    assert three_weekly["effective_demand"] == 450
    assert daily["effective_demand"] == 1000

    assert (
        three_weekly["passengers"]
        < daily["passengers"]
    )


def test_business_market_is_more_frequency_sensitive_than_leisure():

    business_route = pd.Series(
        {
            "route_id": "BUSINESS",
            "market_type": "business",
            "weekly_demand": 1000,
            "average_fare": 100,
            "variable_cost_per_rotation": 5000,
            "weekly_fixed_route_cost": 5000,
            "round_trip_block_hours": 5,
        }
    )

    leisure_route = pd.Series(
        {
            "route_id": "LEISURE",
            "market_type": "leisure",
            "weekly_demand": 1000,
            "average_fare": 100,
            "variable_cost_per_rotation": 5000,
            "weekly_fixed_route_cost": 5000,
            "round_trip_block_hours": 5,
        }
    )

    business = calculate_route_economics(
        route=business_route,
        frequency=3,
        seats=180,
    )

    leisure = calculate_route_economics(
        route=leisure_route,
        frequency=3,
        seats=180,
    )

    # Business passengers are assumed to care more
    # about service frequency.
    assert business["effective_demand"] == 300
    assert leisure["effective_demand"] == 600

    assert (
        business["effective_demand"]
        < leisure["effective_demand"]
    )


def test_daily_frequency_uses_full_base_demand():

    route = pd.Series(
        {
            "route_id": "TEST",
            "market_type": "business",
            "weekly_demand": 1000,
            "average_fare": 100,
            "variable_cost_per_rotation": 5000,
            "weekly_fixed_route_cost": 5000,
            "round_trip_block_hours": 5,
        }
    )

    result = calculate_route_economics(
        route=route,
        frequency=7,
        seats=180,
    )

    assert result["demand_multiplier"] == 1.0
    assert result["effective_demand"] == 1000