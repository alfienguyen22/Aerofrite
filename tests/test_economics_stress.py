import pandas as pd
import pytest

from src.economics import (
    calculate_route_economics,
)


def make_test_route(
    market_type="mixed",
    weekly_demand=1000,
    average_fare=100,
    variable_cost_per_rotation=5000,
    weekly_fixed_route_cost=5000,
    round_trip_block_hours=5,
):
    """
    Create a reusable fictional route for
    economics stress testing.
    """

    return pd.Series(
        {
            "route_id": "TEST",
            "market_type": market_type,
            "weekly_demand": weekly_demand,
            "average_fare": average_fare,
            "variable_cost_per_rotation": (
                variable_cost_per_rotation
            ),
            "weekly_fixed_route_cost": (
                weekly_fixed_route_cost
            ),
            "round_trip_block_hours": (
                round_trip_block_hours
            ),
        }
    )


def test_zero_demand_route_loses_money_if_operated():
    """
    An operated route with zero demand
    should carry no passengers and earn
    no revenue, while still incurring
    operating and fixed route costs.
    """

    route = make_test_route(
        weekly_demand=0,
    )

    result = calculate_route_economics(
        route=route,
        frequency=3,
        seats=180,
    )

    assert result["effective_demand"] == 0
    assert result["passengers"] == 0
    assert result["revenue"] == 0

    assert result["variable_cost"] == 15000
    assert result["fixed_route_cost"] == 5000
    assert result["total_cost"] == 20000

    assert result["contribution"] == -20000

    assert result["aircraft_hours"] == 15


def test_extreme_demand_cannot_exceed_capacity():
    """
    Even enormous demand must not allow
    passengers to exceed physical seat
    capacity.
    """

    route = make_test_route(
        weekly_demand=1_000_000,
    )

    result = calculate_route_economics(
        route=route,
        frequency=7,
        seats=180,
    )

    expected_capacity = (
        7
        * 180
        * 2
    )

    assert result["weekly_seats"] == 2520
    assert result["weekly_seats"] == expected_capacity

    assert result["passengers"] == 2520

    assert (
        result["passengers"]
        <= result["weekly_seats"]
    )

    assert result["load_factor"] == 1.0


def test_extremely_high_cost_route_is_unprofitable():
    """
    A route with extremely high operating
    costs should produce negative contribution.
    """

    route = make_test_route(
        weekly_demand=2000,
        average_fare=100,
        variable_cost_per_rotation=100000,
        weekly_fixed_route_cost=50000,
    )

    result = calculate_route_economics(
        route=route,
        frequency=7,
        seats=180,
    )

    assert result["revenue"] > 0
    assert result["total_cost"] > result["revenue"]

    assert result["contribution"] < 0

    assert (
        result["contribution_per_aircraft_hour"]
        < 0
    )


def test_closed_expensive_route_has_zero_cost():
    """
    Closing a route should prevent both
    variable and fixed route costs from
    being incurred.
    """

    route = make_test_route(
        weekly_demand=5000,
        variable_cost_per_rotation=1_000_000,
        weekly_fixed_route_cost=1_000_000,
    )

    result = calculate_route_economics(
        route=route,
        frequency=0,
        seats=180,
    )

    assert result["passengers"] == 0
    assert result["weekly_seats"] == 0

    assert result["revenue"] == 0
    assert result["variable_cost"] == 0
    assert result["fixed_route_cost"] == 0
    assert result["total_cost"] == 0

    assert result["contribution"] == 0
    assert result["aircraft_hours"] == 0

    assert (
        result["contribution_per_aircraft_hour"]
        == 0
    )


def test_invalid_market_type_is_rejected():
    """
    Economics calculations should reject
    an unknown market classification.
    """

    route = make_test_route(
        market_type="premium_unicorn",
    )

    with pytest.raises(
        ValueError,
        match="Unknown market type",
    ):
        calculate_route_economics(
            route=route,
            frequency=7,
            seats=180,
        )


@pytest.mark.parametrize(
    "invalid_frequency",
    [
        1,
        2,
        5,
        6,
        8,
        20,
    ],
)
def test_unsupported_frequency_is_rejected(
    invalid_frequency,
):
    """
    The economics model should reject
    frequencies for which no demand
    multiplier has been defined.
    """

    route = make_test_route(
        market_type="mixed",
    )

    with pytest.raises(
        ValueError,
        match="No demand multiplier defined",
    ):
        calculate_route_economics(
            route=route,
            frequency=invalid_frequency,
            seats=180,
        )


@pytest.mark.parametrize(
    "market_type",
    [
        "business",
        "mixed",
        "leisure",
    ],
)
def test_all_supported_market_types_work(
    market_type,
):
    """
    Every supported market type should
    calculate successfully at a valid
    frequency.
    """

    route = make_test_route(
        market_type=market_type,
    )

    result = calculate_route_economics(
        route=route,
        frequency=7,
        seats=180,
    )

    assert (
        result["market_type"]
        == market_type
    )

    assert (
        result["demand_multiplier"]
        == 1.0
    )

    assert (
        result["effective_demand"]
        == 1000
    )


def test_aircraft_hours_scale_with_frequency():
    """
    Aircraft-hour consumption should scale
    directly with weekly frequency.
    """

    route = make_test_route(
        round_trip_block_hours=5,
    )

    three_weekly = calculate_route_economics(
        route=route,
        frequency=3,
        seats=180,
    )

    seven_weekly = calculate_route_economics(
        route=route,
        frequency=7,
        seats=180,
    )

    assert (
        three_weekly["aircraft_hours"]
        == 15
    )

    assert (
        seven_weekly["aircraft_hours"]
        == 35
    )

    assert (
        seven_weekly["aircraft_hours"]
        > three_weekly["aircraft_hours"]
    )