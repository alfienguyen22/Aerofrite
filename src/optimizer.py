import pandas as pd

from ortools.sat.python import cp_model

from src.economics import calculate_route_economics

# File path
ROUTES_PATH = "data/routes.csv"
AIRCRAFT_PATH = "data/aircraft.csv"
OUTPUT_PATH = "outputs/results/optimized_network.csv"


def run_toy_optimizer():
    """
    Small test optimization problem.

    Used to understand and validate the optimization logic
    before applying it to the full Aerofrite network.
    """

    routes = {
        "BCN": {
            0: {
                "contribution": 0,
                "aircraft_hours": 0,
            },
            3: {
                "contribution": 45_000,
                "aircraft_hours": 18,
            },
            7: {
                "contribution": 90_000,
                "aircraft_hours": 40,
            },
        },

        "MAD": {
            0: {
                "contribution": 0,
                "aircraft_hours": 0,
            },
            3: {
                "contribution": 40_000,
                "aircraft_hours": 20,
            },
            7: {
                "contribution": 82_000,
                "aircraft_hours": 44,
            },
        },

        "LIS": {
            0: {
                "contribution": 0,
                "aircraft_hours": 0,
            },
            3: {
                "contribution": 48_000,
                "aircraft_hours": 24,
            },
            7: {
                "contribution": 95_000,
                "aircraft_hours": 55,
            },
        },
    }

    available_aircraft_hours = 80

    model = cp_model.CpModel()

    # Creating decision variable
    decision_vars = {}

    # Creating binary variables for each combination
    for route, options in routes.items():

        for frequency in options:

            decision_vars[
                (route, frequency)
            ] = model.NewBoolVar(
                f"{route}_{frequency}"
            )


    # Only one frequency per route
    for route, options in routes.items():

        model.Add(
            sum(
                decision_vars[
                    (route, frequency)
                ]
                for frequency in options
            )
            == 1
        )


    # Converting aircraft hours into minutes
    available_aircraft_minutes = (
        available_aircraft_hours * 60
    )

    # Adding aircraft hours constraint
    total_aircraft_minutes = []

    for route, options in routes.items():

        for frequency, data in options.items():

            aircraft_minutes = round(
                data["aircraft_hours"] * 60
            )

            total_aircraft_minutes.append(
                decision_vars[
                    (route, frequency)
                ]
                * aircraft_minutes
            )

    model.Add(
        sum(total_aircraft_minutes)
        <= available_aircraft_minutes
    )

    # Defining objective
    total_contribution = []

    for route, options in routes.items():

        for frequency, data in options.items():

            contribution = round(
                data["contribution"]
            )

            total_contribution.append(
                decision_vars[
                    (route, frequency)
                ]
                * contribution
            )

    model.Maximize(
        sum(total_contribution)
    )

    solver = cp_model.CpSolver()

    status = solver.Solve(model)

    if status not in (
        cp_model.OPTIMAL,
        cp_model.FEASIBLE,
    ):
        raise RuntimeError(
            "Optimizer could not find a feasible solution."
        )


    results = []

    for route, options in routes.items():

        for frequency, data in options.items():

            variable = decision_vars[
                (route, frequency)
            ]

            if solver.Value(variable) == 1:

                results.append(
                    {
                        "route": route,
                        "frequency": frequency,
                        "contribution": data[
                            "contribution"
                        ],
                        "aircraft_hours": data[
                            "aircraft_hours"
                        ],
                    }
                )

    total_contribution_value = sum(
        result["contribution"]
        for result in results
    )

    total_aircraft_hours = sum(
        result["aircraft_hours"]
        for result in results
    )

    print("\nOptimal network:")
    print("-" * 50)

    for result in results:

        print(
            f"{result['route']:3} | "
            f"{result['frequency']:2}x/week | "
            f"Contribution: "
            f"€{result['contribution']:,.0f} | "
            f"Aircraft hours: "
            f"{result['aircraft_hours']:.1f}"
        )

    print("-" * 50)

    print(
        f"Total contribution: "
        f"€{total_contribution_value:,.0f}"
    )

    print(
        f"Aircraft hours used: "
        f"{total_aircraft_hours:.1f}"
        f" / {available_aircraft_hours}"
    )

    return results

# Actual Optimizer Function
def optimize_network():
    """
    Optimize Aerofrite's weekly route network.

    For every candidate route, choose exactly one
    allowed weekly frequency while respecting total
    fleet aircraft-hour capacity.

    Objective:
        Maximize total weekly network contribution.
    """

    routes = pd.read_csv(ROUTES_PATH)
    aircraft = pd.read_csv(AIRCRAFT_PATH)

    # Load Fleet Assumptions
    aircraft_row = aircraft.iloc[0]

    seats = int(
        aircraft_row["seats"]
    )

    fleet_size = int(
        aircraft_row["fleet_size"]
    )

    usable_hours_per_day = float(
        aircraft_row["usable_hours_per_day"]
    )

    # Calculate Weekly Capacity
    available_aircraft_hours = (
        fleet_size
        * usable_hours_per_day
        * 7
    )

    # Convert to minute
    available_aircraft_minutes = round(
        available_aircraft_hours * 60
    )

    # Build route and frequency combinations
    route_options = {}
    for _, route in routes.iterrows():

        route_id = route["route_id"]

        frequencies = [
            int(value)
            for value in str(
                route["frequency_options"]
            ).split("|")
        ]

        route_options[route_id] = {}

        for frequency in frequencies:

            economics = calculate_route_economics(
                route=route,
                frequency=frequency,
                seats=seats,
            )

            route_options[
                route_id
            ][frequency] = economics

    model = cp_model.CpModel()

    decision_vars = {}

    for route_id, options in route_options.items():

        for frequency in options:

            decision_vars[
                (route_id, frequency)
            ] = model.NewBoolVar(
                f"{route_id}_{frequency}"
            )

    # One frequency per route
    for route_id, options in route_options.items():

        model.Add(
            sum(
                decision_vars[
                    (route_id, frequency)
                ]
                for frequency in options
            )
            == 1
        )

    # Fleet constraint
    aircraft_minute_terms = []

    for route_id, options in route_options.items():

        for frequency, economics in options.items():

            aircraft_minutes = round(
                economics["aircraft_hours"]
                * 60
            )

            aircraft_minute_terms.append(
                decision_vars[
                    (route_id, frequency)
                ]
                * aircraft_minutes
            )

    model.Add(
        sum(aircraft_minute_terms)
        <= available_aircraft_minutes
    )

    contribution_terms = []

    for route_id, options in route_options.items():

        for frequency, economics in options.items():

            contribution = round(
                economics["contribution"]
            )

            contribution_terms.append(
                decision_vars[
                    (route_id, frequency)
                ]
                * contribution
            )

    model.Maximize(
        sum(contribution_terms)
    )

    solver = cp_model.CpSolver()

    status = solver.Solve(model)

    if status not in (
        cp_model.OPTIMAL,
        cp_model.FEASIBLE,
    ):
        raise RuntimeError(
            "No feasible Aerofrite network found."
        )


    selected_routes = []
    selected_aircraft_minutes = 0

    for route_id, options in route_options.items():

        for frequency, economics in options.items():

            variable = decision_vars[
                (route_id, frequency)
            ]

            if solver.Value(variable) == 1:

                selected_routes.append(
                    economics
                )

                aircraft_minutes = round(
                    economics["aircraft_hours"]
                    * 60
                )

                selected_aircraft_minutes += (
                    aircraft_minutes
                )


    results = pd.DataFrame(
        selected_routes
    )

    total_contribution = (
        results["contribution"].sum()
    )

    total_revenue = (
        results["revenue"].sum()
    )

    total_cost = (
        results["total_cost"].sum()
    )

    total_passengers = (
        results["passengers"].sum()
    )

    total_aircraft_hours = (
        selected_aircraft_minutes / 60
    )

    fleet_utilization = (
        total_aircraft_hours
        / available_aircraft_hours
    )

    active_routes = results[
        results["frequency"] > 0
    ]

    destinations_served = len(
        active_routes
    )

    active_routes.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("\n")
    print("=" * 70)
    print("AEROFRITE — OPTIMAL WEEKLY NETWORK")
    print("=" * 70)

    for _, result in results.iterrows():

        route_id = result["route_id"]
        frequency = int(
            result["frequency"]
        )

        if frequency == 0:

            print(
                f"{route_id:8} | "
                f"CLOSED"
            )

        else:

            print(
                f"{route_id:8} | "
                f"{frequency:2}x/week | "
                f"Passengers: "
                f"{int(result['passengers']):5} | "
                f"LF: "
                f"{result['load_factor']:.1%} | "
                f"Contribution: "
                f"€{result['contribution']:,.0f} | "
                f"Hours: "
                f"{result['aircraft_hours']:.1f}"
            )

    print("-" * 70)

    print(
        f"Destinations served: "
        f"{destinations_served}"
    )

    print(
        f"Weekly passengers: "
        f"{int(total_passengers):,}"
    )

    print(
        f"Weekly revenue: "
        f"€{total_revenue:,.0f}"
    )

    print(
        f"Weekly cost: "
        f"€{total_cost:,.0f}"
    )

    print(
        f"Weekly contribution: "
        f"€{total_contribution:,.0f}"
    )

    print(
        f"Aircraft hours: "
        f"{total_aircraft_hours:.1f} "
        f"/ {available_aircraft_hours:.1f}"
    )

    print(
        f"Fleet utilization: "
        f"{fleet_utilization:.1%}"
    )

    print("=" * 70)

    return {
        "routes": results,
        "active_routes": active_routes,
        "total_contribution": total_contribution,
        "total_revenue": total_revenue,
        "total_cost": total_cost,
        "total_passengers": total_passengers,
        "total_aircraft_hours": total_aircraft_hours,
        "available_aircraft_hours": available_aircraft_hours,
        "fleet_utilization": fleet_utilization,
        "destinations_served": destinations_served,
    }

if __name__ == "__main__":
    optimize_network()