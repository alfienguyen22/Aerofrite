from src.scenarios import (
    compare_fleet_scenarios,
    compare_networks,
    compare_season_scenarios,
)


def test_fleet_scenario_summary_contains_all_scenarios():

    summary, results = (
        compare_fleet_scenarios(
            [4, 5, 6]
        )
    )

    assert summary[
        "Fleet Size"
    ].tolist() == [
        4,
        5,
        6,
    ]

    assert set(
        results.keys()
    ) == {
        4,
        5,
        6,
    }


def test_more_fleet_cannot_reduce_optimal_contribution():

    summary, _ = (
        compare_fleet_scenarios(
            [4, 5, 6]
        )
    )

    contributions = summary[
        "Contribution (€)"
    ].tolist()

    assert contributions[1] >= contributions[0]
    assert contributions[2] >= contributions[1]


def test_scenario_capacity_is_respected():

    summary, _ = (
        compare_fleet_scenarios(
            [0, 1, 5, 6]
        )
    )

    for _, row in summary.iterrows():

        assert (
            row["Aircraft Hours"]
            <= row["Available Hours"]
            + 0.01
        )


def test_network_comparison_only_contains_changes():

    _, results = (
        compare_fleet_scenarios(
            [5, 6]
        )
    )

    comparison = compare_networks(
        results[5],
        results[6],
    )

    assert all(
        comparison[
            "Frequency A"
        ]
        != comparison[
            "Frequency B"
        ]
    )


def test_identical_network_has_no_changes():

    _, results = (
        compare_fleet_scenarios(
            [5]
        )
    )

    comparison = compare_networks(
        results[5],
        results[5],
    )

    assert comparison.empty

def test_incremental_metrics_are_calculated():

    summary, _ = (
        compare_fleet_scenarios(
            [4, 5, 6]
        )
    )

    row_5 = summary[
        summary["Fleet Size"] == 5
    ].iloc[0]

    row_6 = summary[
        summary["Fleet Size"] == 6
    ].iloc[0]

    assert (
        row_5[
            "Incremental Contribution (€)"
        ]
        > 0
    )

    assert (
        row_6[
            "Incremental Contribution (€)"
        ]
        > 0
    )

    assert (
        row_5[
            "Incremental Aircraft Hours"
        ]
        > 0
    )

    assert (
        row_6[
            "Incremental Aircraft Hours"
        ]
        > 0
    )

    assert (
        row_5[
            "Incremental Contribution / Hour (€)"
        ]
        > 0
    )

    assert (
        row_6[
            "Incremental Contribution / Hour (€)"
        ]
        > 0
    )

def test_season_scenarios_include_all_seasons():

    summary, results = (
        compare_season_scenarios(
            fleet_size=5,
        )
    )

    assert summary[
        "Season"
    ].tolist() == [
        "Winter",
        "Shoulder",
        "Summer",
    ]

    assert set(
        results.keys()
    ) == {
        "winter",
        "shoulder",
        "summer",
    }


def test_season_scenarios_respect_capacity():

    summary, _ = (
        compare_season_scenarios(
            fleet_size=5,
        )
    )

    for _, row in summary.iterrows():

        assert (
            row["Aircraft Hours"]
            <= row["Available Hours"]
            + 0.01
        )