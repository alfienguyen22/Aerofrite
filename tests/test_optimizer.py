from src.optimizer import run_toy_optimizer
from src.optimizer import optimize_network


def test_toy_optimizer_respects_capacity():

    results = run_toy_optimizer()

    total_hours = sum(
        result["aircraft_hours"]
        for result in results
    )

    assert total_hours <= 80

def test_network_optimizer_respects_fleet_capacity():

    result = optimize_network()

    assert (
        result["total_aircraft_hours"]
        <= result["available_aircraft_hours"]
    )

def test_optimizer_selects_one_option_per_route():

    result = optimize_network()

    routes = result["routes"]

    assert len(routes) == 10

