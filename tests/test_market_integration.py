from src.economics import (
    calculate_route_economics,
)


def make_route(
    competition_level="low",
):
    return {
        "route_id": "BRU-TEST",
        "market_type": "leisure",
        "competition_level": (
            competition_level
        ),
        "weekly_demand": 1000,
        "average_fare": 100,
        "variable_cost_per_rotation": 5000,
        "weekly_fixed_route_cost": 5000,
        "round_trip_block_hours": 5,
    }


def test_summer_increases_leisure_demand():

    route = make_route()

    winter = calculate_route_economics(
        route=route,
        frequency=7,
        seats=180,
        season="winter",
    )

    summer = calculate_route_economics(
        route=route,
        frequency=7,
        seats=180,
        season="summer",
    )

    assert (
        summer["adjusted_market_demand"]
        > winter["adjusted_market_demand"]
    )

    assert (
        summer["effective_demand"]
        > winter["effective_demand"]
    )


def test_high_competition_reduces_demand():

    low_competition = (
        calculate_route_economics(
            route=make_route(
                competition_level="low",
            ),
            frequency=7,
            seats=180,
            season="shoulder",
        )
    )

    high_competition = (
        calculate_route_economics(
            route=make_route(
                competition_level="high",
            ),
            frequency=7,
            seats=180,
            season="shoulder",
        )
    )

    assert (
        high_competition[
            "effective_demand"
        ]
        < low_competition[
            "effective_demand"
        ]
    )


def test_shoulder_low_competition_preserves_base_demand():

    result = calculate_route_economics(
        route=make_route(),
        frequency=7,
        seats=180,
        season="shoulder",
    )

    assert (
        result["adjusted_market_demand"]
        == 1000
    )

    assert (
        result["effective_demand"]
        == 1000
    )


def test_summer_can_increase_contribution():

    route = make_route()

    winter = calculate_route_economics(
        route=route,
        frequency=7,
        seats=180,
        season="winter",
    )

    summer = calculate_route_economics(
        route=route,
        frequency=7,
        seats=180,
        season="summer",
    )

    assert (
        summer["contribution"]
        > winter["contribution"]
    )