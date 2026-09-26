import pytest

from src.optimizer import optimize_network


def test_zero_buffer_preserves_full_capacity():

    result = optimize_network(
        fleet_size_override=5,
        operational_buffer=0.0,
        save_output=False,
        print_results=False,
    )

    assert (
        result[
            "theoretical_aircraft_hours"
        ]
        == pytest.approx(385.0)
    )

    assert (
        result[
            "available_aircraft_hours"
        ]
        == pytest.approx(385.0)
    )


def test_ten_percent_buffer_reduces_capacity():

    result = optimize_network(
        fleet_size_override=5,
        operational_buffer=0.10,
        save_output=False,
        print_results=False,
    )

    assert (
        result[
            "theoretical_aircraft_hours"
        ]
        == pytest.approx(385.0)
    )

    assert (
        result[
            "reserved_aircraft_hours"
        ]
        == pytest.approx(38.5)
    )

    assert (
        result[
            "available_aircraft_hours"
        ]
        == pytest.approx(346.5)
    )


def test_buffered_network_respects_capacity():

    result = optimize_network(
        fleet_size_override=5,
        operational_buffer=0.10,
        save_output=False,
        print_results=False,
    )

    assert (
        result[
            "total_aircraft_hours"
        ]
        <= result[
            "available_aircraft_hours"
        ]
        + 0.01
    )


def test_more_buffer_cannot_increase_capacity():

    no_buffer = optimize_network(
        fleet_size_override=5,
        operational_buffer=0.0,
        save_output=False,
        print_results=False,
    )

    buffered = optimize_network(
        fleet_size_override=5,
        operational_buffer=0.20,
        save_output=False,
        print_results=False,
    )

    assert (
        buffered[
            "available_aircraft_hours"
        ]
        < no_buffer[
            "available_aircraft_hours"
        ]
    )


def test_invalid_negative_buffer_rejected():

    with pytest.raises(ValueError):

        optimize_network(
            operational_buffer=-0.10,
            save_output=False,
            print_results=False,
        )


def test_invalid_full_buffer_rejected():

    with pytest.raises(ValueError):

        optimize_network(
            operational_buffer=1.0,
            save_output=False,
            print_results=False,
        )