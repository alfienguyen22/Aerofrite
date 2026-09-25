import pandas as pd
import pytest

from src.optimizer import optimize_network


ROUTES_PATH = "data/routes.csv"
AIRCRAFT_PATH = "data/aircraft.csv"


def run_stress_case(fleet_size):
    """
    Run the network optimizer silently without
    overwriting the normal optimized network output.
    """

    return optimize_network(
        fleet_size_override=fleet_size,
        save_output=False,
        print_results=False,
    )


def expected_weekly_capacity(fleet_size):
    """
    Calculate expected weekly aircraft-hour capacity
    using the assumptions stored in aircraft.csv.
    """

    aircraft = pd.read_csv(
        AIRCRAFT_PATH
    )

    usable_hours_per_day = float(
        aircraft.iloc[0][
            "usable_hours_per_day"
        ]
    )

    return (
        fleet_size
        * usable_hours_per_day
        * 7
    )


def test_zero_aircraft_closes_entire_network():
    """
    With no aircraft available, every route
    should be closed and all network totals
    should be zero.
    """

    result = run_stress_case(
        fleet_size=0
    )

    assert result["fleet_size"] == 0

    assert (
        result["available_aircraft_hours"]
        == 0
    )

    assert (
        result["total_aircraft_hours"]
        == 0
    )

    assert (
        result["destinations_served"]
        == 0
    )

    assert (
        result["total_passengers"]
        == 0
    )

    assert (
        result["total_revenue"]
        == 0
    )

    assert (
        result["total_cost"]
        == 0
    )

    assert (
        result["total_contribution"]
        == 0
    )

    assert (
        result["routes"]["frequency"]
        == 0
    ).all()


def test_one_aircraft_respects_capacity():
    """
    A one-aircraft Aerofrite network should
    still find a feasible solution without
    exceeding available aircraft hours.
    """

    result = run_stress_case(
        fleet_size=1
    )

    expected_capacity = (
        expected_weekly_capacity(
            fleet_size=1
        )
    )

    assert (
        result["available_aircraft_hours"]
        == expected_capacity
    )

    assert (
        result["total_aircraft_hours"]
        <= result[
            "available_aircraft_hours"
        ]
    )

    assert (
        result["fleet_utilization"]
        <= 1.0
    )

    # With the current Aerofrite economics,
    # at least one profitable service should
    # still be possible with one aircraft.
    assert (
        result["destinations_served"]
        > 0
    )

    assert (
        result["total_contribution"]
        > 0
    )


def test_more_aircraft_cannot_reduce_optimal_contribution():
    """
    Increasing fleet capacity expands the
    optimizer's feasible solution space.

    Therefore, optimal contribution should
    never decrease solely because another
    aircraft becomes available.
    """

    one_aircraft = run_stress_case(
        fleet_size=1
    )

    five_aircraft = run_stress_case(
        fleet_size=5
    )

    six_aircraft = run_stress_case(
        fleet_size=6
    )

    assert (
        round(
            five_aircraft[
                "total_contribution"
            ]
        )
        >= round(
            one_aircraft[
                "total_contribution"
            ]
        )
    )

    assert (
        round(
            six_aircraft[
                "total_contribution"
            ]
        )
        >= round(
            five_aircraft[
                "total_contribution"
            ]
        )
    )


@pytest.mark.parametrize(
    "fleet_size",
    [
        0,
        1,
        2,
        5,
        6,
        10,
    ],
)
def test_capacity_constraint_under_multiple_fleet_sizes(
    fleet_size,
):
    """
    The fleet-hour constraint must hold
    across a range of fleet sizes.
    """

    result = run_stress_case(
        fleet_size=fleet_size
    )

    expected_capacity = (
        expected_weekly_capacity(
            fleet_size=fleet_size
        )
    )

    assert (
        result["available_aircraft_hours"]
        == expected_capacity
    )

    assert (
        result["total_aircraft_hours"]
        <= result[
            "available_aircraft_hours"
        ]
    )

    assert (
        0
        <= result["fleet_utilization"]
        <= 1.0
    )


@pytest.mark.parametrize(
    "fleet_size",
    [
        0,
        1,
        5,
        6,
        10,
    ],
)
def test_optimizer_selects_exactly_one_option_per_route(
    fleet_size,
):
    """
    Every candidate route must have exactly
    one selected decision:

    either CLOSED (frequency 0) or one
    permitted operating frequency.
    """

    source_routes = pd.read_csv(
        ROUTES_PATH
    )

    result = run_stress_case(
        fleet_size=fleet_size
    )

    selected_routes = result[
        "routes"
    ]

    assert (
        len(selected_routes)
        == len(source_routes)
    )

    assert (
        selected_routes[
            "route_id"
        ].is_unique
    )

    assert (
        set(
            selected_routes[
                "route_id"
            ]
        )
        == set(
            source_routes[
                "route_id"
            ]
        )
    )


@pytest.mark.parametrize(
    "fleet_size",
    [
        0,
        1,
        5,
        6,
        10,
    ],
)
def test_selected_frequencies_are_allowed(
    fleet_size,
):
    """
    The optimizer must never invent a
    frequency that is not permitted for
    the route.
    """

    source_routes = pd.read_csv(
        ROUTES_PATH
    )

    result = run_stress_case(
        fleet_size=fleet_size
    )

    selected_routes = result[
        "routes"
    ]

    allowed_frequencies = {}

    for _, route in source_routes.iterrows():

        allowed_frequencies[
            route["route_id"]
        ] = {
            int(value)
            for value in str(
                route[
                    "frequency_options"
                ]
            ).split("|")
        }

    for _, route in selected_routes.iterrows():

        route_id = route[
            "route_id"
        ]

        frequency = int(
            route["frequency"]
        )

        assert (
            frequency
            in allowed_frequencies[
                route_id
            ]
        )


@pytest.mark.parametrize(
    "invalid_fleet_size",
    [
        -1,
        2.5,
        "5",
    ],
)
def test_invalid_fleet_size_is_rejected(
    invalid_fleet_size,
):
    """
    Fleet-size overrides must be
    non-negative integers.
    """

    with pytest.raises(
        ValueError
    ):
        optimize_network(
            fleet_size_override=(
                invalid_fleet_size
            ),
            save_output=False,
            print_results=False,
        )