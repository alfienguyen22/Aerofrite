import pandas as pd

from src.optimizer import optimize_network
from src.scenarios import compare_networks


# --------------------------------------------------
# Case-study assumptions
# --------------------------------------------------

CASE_STUDY_FLEET_SIZE = 5
CASE_STUDY_OPERATIONAL_BUFFER = 0.10


# --------------------------------------------------
# Build case study
# --------------------------------------------------

def build_case_study():
    """
    Build the main Aerofrite planning case study.

    The case study compares a five-aircraft network
    across winter, shoulder, and summer while holding
    a 10% operational reserve constant.

    Returns
    -------
    dict
        Case-study results, summaries, and network
        comparisons.
    """

    seasons = [
        "winter",
        "shoulder",
        "summer",
    ]

    results = {}

    # --------------------------------------------------
    # Optimize each season
    # --------------------------------------------------

    for season in seasons:

        results[season] = optimize_network(
            fleet_size_override=(
                CASE_STUDY_FLEET_SIZE
            ),
            season=season,
            operational_buffer=(
                CASE_STUDY_OPERATIONAL_BUFFER
            ),
            save_output=False,
            print_results=False,
        )

    # --------------------------------------------------
    # Seasonal summary
    # --------------------------------------------------

    summary_rows = []

    for season in seasons:

        result = results[season]

        summary_rows.append(
            {
                "Season":
                    season.title(),

                "Destinations":
                    result[
                        "destinations_served"
                    ],

                "Passengers":
                    result[
                        "total_passengers"
                    ],

                "Revenue (€)":
                    result[
                        "total_revenue"
                    ],

                "Cost (€)":
                    result[
                        "total_cost"
                    ],

                "Contribution (€)":
                    result[
                        "total_contribution"
                    ],

                "Scheduled Hours":
                    result[
                        "total_aircraft_hours"
                    ],

                "Planning Capacity":
                    result[
                        "available_aircraft_hours"
                    ],

                "Planning Utilization (%)":
                    (
                        result[
                            "fleet_utilization"
                        ]
                        * 100
                    ),
            }
        )

    seasonal_summary = pd.DataFrame(
        summary_rows
    )

    # --------------------------------------------------
    # Winter → Summer network changes
    # --------------------------------------------------

    winter_to_summer = compare_networks(
        results["winter"],
        results["summer"],
    )

    # --------------------------------------------------
    # Shoulder-season resilience comparison
    # --------------------------------------------------

    no_reserve = optimize_network(
        fleet_size_override=(
            CASE_STUDY_FLEET_SIZE
        ),
        season="shoulder",
        operational_buffer=0.0,
        save_output=False,
        print_results=False,
    )

    ten_percent_reserve = (
        results["shoulder"]
    )

    resilience_summary = pd.DataFrame(
        [
            {
                "Scenario":
                    "0% Reserve",

                "Destinations":
                    no_reserve[
                        "destinations_served"
                    ],

                "Passengers":
                    no_reserve[
                        "total_passengers"
                    ],

                "Contribution (€)":
                    no_reserve[
                        "total_contribution"
                    ],

                "Planning Capacity":
                    no_reserve[
                        "available_aircraft_hours"
                    ],

                "Scheduled Hours":
                    no_reserve[
                        "total_aircraft_hours"
                    ],
            },
            {
                "Scenario":
                    "10% Reserve",

                "Destinations":
                    ten_percent_reserve[
                        "destinations_served"
                    ],

                "Passengers":
                    ten_percent_reserve[
                        "total_passengers"
                    ],

                "Contribution (€)":
                    ten_percent_reserve[
                        "total_contribution"
                    ],

                "Planning Capacity":
                    ten_percent_reserve[
                        "available_aircraft_hours"
                    ],

                "Scheduled Hours":
                    ten_percent_reserve[
                        "total_aircraft_hours"
                    ],
            },
        ]
    )

    # --------------------------------------------------
    # Calculate headline changes
    # --------------------------------------------------

    winter_result = results["winter"]
    summer_result = results["summer"]

    seasonal_impact = {
        "passenger_change": int(
            summer_result[
                "total_passengers"
            ]
            - winter_result[
                "total_passengers"
            ]
        ),

        "contribution_change": float(
            summer_result[
                "total_contribution"
            ]
            - winter_result[
                "total_contribution"
            ]
        ),

        "destination_change": int(
            summer_result[
                "destinations_served"
            ]
            - winter_result[
                "destinations_served"
            ]
        ),
    }

    resilience_impact = {
        "passenger_change": int(
            ten_percent_reserve[
                "total_passengers"
            ]
            - no_reserve[
                "total_passengers"
            ]
        ),

        "contribution_change": float(
            ten_percent_reserve[
                "total_contribution"
            ]
            - no_reserve[
                "total_contribution"
            ]
        ),

        "destination_change": int(
            ten_percent_reserve[
                "destinations_served"
            ]
            - no_reserve[
                "destinations_served"
            ]
        ),

        "reserved_hours": float(
            ten_percent_reserve[
                "reserved_aircraft_hours"
            ]
        ),
    }

    return {
        "fleet_size":
            CASE_STUDY_FLEET_SIZE,

        "operational_buffer":
            CASE_STUDY_OPERATIONAL_BUFFER,

        "results":
            results,

        "seasonal_summary":
            seasonal_summary,

        "winter_to_summer":
            winter_to_summer,

        "seasonal_impact":
            seasonal_impact,

        "resilience_summary":
            resilience_summary,

        "resilience_impact":
            resilience_impact,
    }