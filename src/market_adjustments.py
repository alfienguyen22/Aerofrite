# --------------------------------------------------
# Aerofrite commercial market adjustments
# --------------------------------------------------

# Competition affects the share of underlying
# market demand Aerofrite can reasonably capture.
#
# These are transparent modeling assumptions,
# not empirically calibrated market-share estimates.

COMPETITION_MULTIPLIERS = {
    "low": 1.00,
    "medium": 0.90,
    "high": 0.80,
}


# --------------------------------------------------
# Seasonal demand assumptions
# --------------------------------------------------
#
# Seasonality varies by market type.
#
# Shoulder season is the baseline scenario.

SEASONALITY_MULTIPLIERS = {
    "business": {
        "winter": 1.00,
        "shoulder": 1.00,
        "summer": 0.95,
    },
    "mixed": {
        "winter": 0.95,
        "shoulder": 1.00,
        "summer": 1.10,
    },
    "leisure": {
        "winter": 0.80,
        "shoulder": 1.00,
        "summer": 1.25,
    },
}


def get_competition_multiplier(
    competition_level,
):
    """
    Return the modeled demand multiplier
    associated with route competition.
    """

    if competition_level not in (
        COMPETITION_MULTIPLIERS
    ):

        raise ValueError(
            "Unknown competition level: "
            f"{competition_level}"
        )

    return COMPETITION_MULTIPLIERS[
        competition_level
    ]


def get_seasonality_multiplier(
    market_type,
    season,
):
    """
    Return the modeled seasonal demand
    multiplier for a market type.
    """

    if market_type not in (
        SEASONALITY_MULTIPLIERS
    ):

        raise ValueError(
            f"Unknown market type: {market_type}"
        )

    if season not in (
        SEASONALITY_MULTIPLIERS[
            market_type
        ]
    ):

        raise ValueError(
            f"Unknown season: {season}"
        )

    return (
        SEASONALITY_MULTIPLIERS[
            market_type
        ][season]
    )


def calculate_adjusted_market_demand(
    base_weekly_demand,
    market_type,
    competition_level,
    season,
):
    """
    Adjust base market demand for seasonality
    and competition.

    Frequency sensitivity is intentionally
    applied separately by the demand model.
    """

    if base_weekly_demand < 0:

        raise ValueError(
            "Base weekly demand cannot be negative."
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

    adjusted_demand = round(
        base_weekly_demand
        * seasonality_multiplier
        * competition_multiplier
    )

    return adjusted_demand