import pandas as pd

from src.optimizer import optimize_network


def compare_fleet_scenarios(fleet_sizes, season="shoulder",):
    """
    Run the Aerofrite optimizer for multiple fleet sizes.

    Parameters
    ----------
    fleet_sizes : list[int]
        Fleet sizes to evaluate.

    Returns
    -------
    summary : pandas.DataFrame
        One row per fleet-size scenario.

    results : dict
        Full optimizer result for each fleet size.
        Example:
            results[5]
    """

    if not fleet_sizes:
        raise ValueError(
            "At least one fleet size is required."
        )

    if any(
        not isinstance(fleet_size, int)
        or fleet_size < 0
        for fleet_size in fleet_sizes
    ):
        raise ValueError(
            "Fleet sizes must be non-negative integers."
        )

    # Remove duplicates and keep scenarios ordered.
    fleet_sizes = sorted(
        set(fleet_sizes)
    )

    summary_rows = []
    results = {}

    for fleet_size in fleet_sizes:

        result = optimize_network(
            fleet_size_override=fleet_size,
            season=season,
            save_output=False,
            print_results=False,
        )

        results[fleet_size] = result

        summary_rows.append(
            {
                "Fleet Size": fleet_size,
                "Destinations": result[
                    "destinations_served"
                ],
                "Passengers": result[
                    "total_passengers"
                ],
                "Revenue (€)": result[
                    "total_revenue"
                ],
                "Cost (€)": result[
                    "total_cost"
                ],
                "Contribution (€)": result[
                    "total_contribution"
                ],
                "Aircraft Hours": result[
                    "total_aircraft_hours"
                ],
                "Available Hours": result[
                    "available_aircraft_hours"
                ],
                "Utilization": (
                    result[
                        "fleet_utilization"
                    ]
                    * 100
                ),
            }
        )

    summary = pd.DataFrame(
        summary_rows
    )

    # --------------------------------------------------
    # Incremental value of additional aircraft
    # --------------------------------------------------

    summary[
        "Incremental Contribution (€)"
    ] = summary[
        "Contribution (€)"
    ].diff()

    summary[
        "Incremental Passengers"
    ] = summary[
        "Passengers"
    ].diff()

    summary[
        "Incremental Destinations"
    ] = summary[
        "Destinations"
    ].diff()

    summary[
    "Incremental Aircraft Hours"
    ] = summary[
        "Aircraft Hours"
    ].diff()

    summary[
        "Incremental Contribution / Hour (€)"
    ] = (
    summary[
        "Incremental Contribution (€)"
    ]
    / summary[
        "Incremental Aircraft Hours"
    ]
)

    return summary, results


def compare_networks(
    result_a,
    result_b,
):
    """
    Compare route frequencies between two
    optimized network scenarios.

    Returns only routes whose frequency changed.
    """

    network_a = result_a[
        "routes"
    ][
        [
            "route_id",
            "frequency",
        ]
    ].copy()

    network_b = result_b[
        "routes"
    ][
        [
            "route_id",
            "frequency",
        ]
    ].copy()

    network_a = network_a.rename(
        columns={
            "frequency": "Frequency A",
        }
    )

    network_b = network_b.rename(
        columns={
            "frequency": "Frequency B",
        }
    )

    comparison = network_a.merge(
        network_b,
        on="route_id",
        how="outer",
    )

    comparison[
        "Frequency A"
    ] = (
        comparison["Frequency A"]
        .fillna(0)
        .astype(int)
    )

    comparison[
        "Frequency B"
    ] = (
        comparison["Frequency B"]
        .fillna(0)
        .astype(int)
    )

    comparison[
        "Frequency Change"
    ] = (
        comparison["Frequency B"]
        - comparison["Frequency A"]
    )

    # Only keep routes that actually changed.
    comparison = comparison[
        comparison["Frequency Change"] != 0
    ].copy()

    def classify_change(row):

        old_frequency = row[
            "Frequency A"
        ]

        new_frequency = row[
            "Frequency B"
        ]

        if (
            old_frequency == 0
            and new_frequency > 0
        ):
            return "Route added"

        if (
            old_frequency > 0
            and new_frequency == 0
        ):
            return "Route removed"

        if new_frequency > old_frequency:
            return "Frequency increased"

        return "Frequency decreased"

    comparison[
        "Change Type"
    ] = comparison.apply(
        classify_change,
        axis=1,
    )

    comparison = comparison.rename(
        columns={
            "route_id": "Route",
        }
    )

    return comparison.sort_values(
        by=[
            "Change Type",
            "Route",
        ]
    )