import pytest

from src.demand import (
    calculate_effective_demand,
    get_frequency_multiplier,
)


def test_daily_frequency_is_baseline_for_all_markets():

    for market_type in [
        "business",
        "mixed",
        "leisure",
    ]:

        multiplier = (
            get_frequency_multiplier(
                market_type,
                7,
            )
        )

        assert multiplier == 1.0


def test_business_is_more_frequency_sensitive():

    business = (
        get_frequency_multiplier(
            "business",
            3,
        )
    )

    mixed = (
        get_frequency_multiplier(
            "mixed",
            3,
        )
    )

    leisure = (
        get_frequency_multiplier(
            "leisure",
            3,
        )
    )

    assert business < mixed
    assert mixed < leisure


@pytest.mark.parametrize(
    "market_type",
    [
        "business",
        "mixed",
        "leisure",
    ],
)
def test_demand_does_not_decrease_with_frequency(
    market_type,
):

    frequencies = [
        0,
        3,
        4,
        7,
        10,
        14,
    ]

    multipliers = [
        get_frequency_multiplier(
            market_type,
            frequency,
        )
        for frequency in frequencies
    ]

    assert multipliers == sorted(
        multipliers
    )


def test_business_effective_demand_at_three_weekly():

    demand = (
        calculate_effective_demand(
            base_weekly_demand=1000,
            market_type="business",
            frequency=3,
        )
    )

    assert demand == 300


def test_mixed_effective_demand_at_four_weekly():

    demand = (
        calculate_effective_demand(
            base_weekly_demand=1000,
            market_type="mixed",
            frequency=4,
        )
    )

    assert demand == 600


def test_leisure_effective_demand_at_three_weekly():

    demand = (
        calculate_effective_demand(
            base_weekly_demand=1000,
            market_type="leisure",
            frequency=3,
        )
    )

    assert demand == 600


def test_zero_frequency_produces_zero_demand():

    demand = (
        calculate_effective_demand(
            base_weekly_demand=2000,
            market_type="mixed",
            frequency=0,
        )
    )

    assert demand == 0


def test_high_frequency_can_capture_more_than_baseline():

    demand = (
        calculate_effective_demand(
            base_weekly_demand=1000,
            market_type="business",
            frequency=14,
        )
    )

    assert demand == 1250


def test_invalid_market_type_is_rejected():

    with pytest.raises(ValueError):

        get_frequency_multiplier(
            "unknown",
            7,
        )


def test_invalid_frequency_is_rejected():

    with pytest.raises(ValueError):

        get_frequency_multiplier(
            "business",
            5,
        )


def test_negative_base_demand_is_rejected():

    with pytest.raises(ValueError):

        calculate_effective_demand(
            base_weekly_demand=-100,
            market_type="mixed",
            frequency=7,
        )