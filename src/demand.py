# --------------------------------------------------
# Frequency-sensitive demand model
# --------------------------------------------------

FREQUENCY_DEMAND_MULTIPLIERS = {
    "business": {
        0: 0.00,
        3: 0.30,
        4: 0.45,
        7: 1.00,
        10: 1.12,
        14: 1.25,
    },
    "mixed": {
        0: 0.00,
        3: 0.45,
        4: 0.60,
        7: 1.00,
        10: 1.08,
        14: 1.15,
    },
    "leisure": {
        0: 0.00,
        3: 0.60,
        4: 0.75,
        7: 1.00,
        10: 1.04,
        14: 1.08,
    },
}


def get_frequency_multiplier(
    market_type,
    frequency,
):
    """
    Return the modeled demand multiplier for a
    market type and weekly frequency.

    Examples
    --------
    Business market at 3x weekly:
        0.30

    Leisure market at 3x weekly:
        0.60

    All markets at 7x weekly:
        1.00
    """

    if market_type not in FREQUENCY_DEMAND_MULTIPLIERS:

        raise ValueError(
            f"Unknown market type: {market_type}"
        )

    market_multipliers = (
        FREQUENCY_DEMAND_MULTIPLIERS[
            market_type
        ]
    )

    if frequency not in market_multipliers:

        raise ValueError(
            f"Unsupported frequency "
            f"{frequency} for market type "
            f"{market_type}."
        )

    return market_multipliers[
        frequency
    ]


def calculate_effective_demand(
    base_weekly_demand,
    market_type,
    frequency,
):
    """
    Calculate demand captured after applying
    Aerofrite's frequency-sensitive demand model.
    """

    if base_weekly_demand < 0:

        raise ValueError(
            "Base weekly demand cannot be negative."
        )

    multiplier = get_frequency_multiplier(
        market_type=market_type,
        frequency=frequency,
    )

    effective_demand = round(
        base_weekly_demand
        * multiplier
    )

    return effective_demand


def build_frequency_curve():
    """
    Return frequency-response assumptions in a
    simple list of dictionaries for analysis and
    visualization.
    """

    rows = []

    for (
        market_type,
        frequency_values,
    ) in FREQUENCY_DEMAND_MULTIPLIERS.items():

        for (
            frequency,
            multiplier,
        ) in frequency_values.items():

            rows.append(
                {
                    "Market Type":
                        market_type,
                    "Weekly Frequency":
                        frequency,
                    "Demand Multiplier":
                        multiplier,
                    "Demand Capture (%)":
                        multiplier * 100,
                }
            )

    return rows