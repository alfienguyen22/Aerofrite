from src.case_study import (
    build_case_study,
)


def test_case_study_uses_five_aircraft():

    case_study = build_case_study()

    assert (
        case_study["fleet_size"]
        == 5
    )


def test_case_study_uses_ten_percent_reserve():

    case_study = build_case_study()

    assert (
        case_study[
            "operational_buffer"
        ]
        == 0.10
    )


def test_case_study_contains_all_seasons():

    case_study = build_case_study()

    assert set(
        case_study[
            "results"
        ].keys()
    ) == {
        "winter",
        "shoulder",
        "summer",
    }


def test_case_study_seasonal_summary():

    case_study = build_case_study()

    summary = case_study[
        "seasonal_summary"
    ]

    assert summary[
        "Season"
    ].tolist() == [
        "Winter",
        "Shoulder",
        "Summer",
    ]


def test_case_study_networks_respect_capacity():

    case_study = build_case_study()

    for result in (
        case_study[
            "results"
        ].values()
    ):

        assert (
            result[
                "total_aircraft_hours"
            ]
            <= result[
                "available_aircraft_hours"
            ]
            + 0.01
        )


def test_case_study_has_network_comparison():

    case_study = build_case_study()

    assert (
        "winter_to_summer"
        in case_study
    )


def test_case_study_has_resilience_comparison():

    case_study = build_case_study()

    assert (
        len(
            case_study[
                "resilience_summary"
            ]
        )
        == 2
    )