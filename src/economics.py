import pandas as pd

# File Path
ROUTES_PATH = "data/routes.csv"
AIRCRAFT_PATH = "data/aircraft.csv"

# Economics Function
def calculate_route_economics(route, frequency, seats,):
    """
    Calculate the weekly economics of one route
    at a given round-trip frequency.

    Parameters
    ----------
    route : pandas Series
        One row from routes.csv.

    frequency : int
        Number of weekly round trips.

    seats : int
        Seats per aircraft.

    Returns
    -------
    dict
        Route economics for the selected frequency.
    """

    # IF not flying route, then return 0
    if frequency == 0:
        return {
            "route_id": route["route_id"],
            "frequency": 0,
            "weekly_seats": 0,
            "passengers": 0,
            "load_factor": 0.0,
            "revenue": 0.0,
            "variable_cost": 0.0,
            "fixed_route_cost": 0.0,
            "total_cost": 0.0,
            "contribution": 0.0,
            "aircraft_hours": 0.0,
        }

    # Calculating Weekly Seats based on Rotation
    weekly_seats = (frequency * seats * 2)

    # Calculating Passengers based on the lower value
    passengers = min(route["weekly_demand"], weekly_seats,)

    load_factor = (passengers / weekly_seats)

    # Calculate Revenue
    revenue = (passengers * route["average_fare"])

    # Calculate Variable Cost
    variable_cost = (frequency * route["variable_cost_per_rotation"])

    # Calculate Fixed Route Cost
    fixed_route_cost = (route["weekly_fixed_route_cost"])

    # Calculate Total Cost
    total_cost = (variable_cost + fixed_route_cost)

    # Calculate Total Contribution
    contribution = (revenue - total_cost)

    # Calculate Aircraft Hours
    aircraft_hours = (frequency * route["round_trip_block_hours"])
    
    contribution_per_aircraft_hour = (
    contribution / aircraft_hours
    if aircraft_hours > 0
    else 0)

    # Return Results
    return {
        "route_id": route["route_id"],
        "frequency": frequency,
        "weekly_seats": int(weekly_seats),
        "passengers": int(passengers),
        "load_factor": round(load_factor, 4),
        "revenue": round(revenue, 2),
        "variable_cost": round(variable_cost, 2),
        "fixed_route_cost": round(
            fixed_route_cost,
            2,
        ),
        "total_cost": round(total_cost, 2),
        "contribution": round(
            contribution,
            2,
        ),
        "aircraft_hours": round(
            aircraft_hours,
            2,
        ),    
        "contribution_per_aircraft_hour": round(
            contribution_per_aircraft_hour,
            2,
        ),
    }

# Create a function to evaluate the route
def evaluate_route(
    destination,
    frequency,
):
    """
    Load Aerofrite data and evaluate one route.
    """

    routes = pd.read_csv(ROUTES_PATH)
    aircraft = pd.read_csv(AIRCRAFT_PATH)

    route_rows = routes[
        routes["destination"] == destination
    ]

    if len(route_rows) != 1:
        raise ValueError(
            f"Expected exactly one route for "
            f"{destination}, "
            f"found {len(route_rows)}"
        )

    route = route_rows.iloc[0]

    aircraft_row = aircraft.iloc[0]
    seats = int(aircraft_row["seats"])

    allowed_frequencies = [
        int(value)
        for value in str(
            route["frequency_options"]
        ).split("|")
    ]

    if frequency not in allowed_frequencies:
        raise ValueError(
            f"Frequency {frequency} is not allowed "
            f"for {destination}. "
            f"Allowed frequencies: "
            f"{allowed_frequencies}"
        )

    return calculate_route_economics(
        route=route,
        frequency=frequency,
        seats=seats,
    )