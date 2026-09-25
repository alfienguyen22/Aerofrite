import math
import pandas as pd

# PROJECT FILES
AIRPORTS_PATH = "data/airports.csv"
AIRCRAFT_PATH = "data/aircraft.csv"
OUTPUT_PATH = "data/routes.csv"

# Defining hubs + destination airports
HUB = "BRU"

DESTINATIONS = [
    "LHR",
    "BCN",
    "MAD",
    "LIS",
    "FCO",
    "CPH",
    "ARN",
    "PRG",
    "ATH",
    "AGP",
]

# Allowed Frequencies
FREQUENCY_OPTIONS = [0, 3, 4, 7, 10, 14]

# Calculate Distance
def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate great-circle distance between two points
    on Earth using latitude and longitude.

    Returns distance in kilometers.
    """

    earth_radius_km = 6371.0

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad)
        * math.cos(lat2_rad)
        * math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.asin(math.sqrt(a))

    return earth_radius_km * c


# Calculating Block Time
def estimate_block_time(distance_km):
    """
    Estimate one-way scheduled block time in hours.

    This is a simplified planning approximation,
    not an observed airline schedule.
    """

    cruise_component = distance_km / 750
    operational_allowance = 0.55

    return round(cruise_component + operational_allowance, 2)

# Load Datasets
airports = pd.read_csv(AIRPORTS_PATH)
aircraft = pd.read_csv(AIRCRAFT_PATH)

aircraft_row = aircraft.iloc[0]

aircraft_type = aircraft_row["aircraft_type"]
planning_range_km = aircraft_row["planning_range_km"]
turnaround_minutes = aircraft_row["turnaround_minutes"]

# Finding/Adding Brussels as hub
hub_rows = airports[airports["iata"] == HUB]

if len(hub_rows) != 1:
    raise ValueError(
        f"Expected exactly one airport for hub {HUB}, "
        f"found {len(hub_rows)}"
    )

hub = hub_rows.iloc[0]

# Somewhere to store routes
route_rows = []

# Collect destination info
for destination_code in DESTINATIONS:

    destination_rows = airports[
        airports["iata"] == destination_code
    ]

    if len(destination_rows) != 1:
        raise ValueError(
            f"Expected exactly one airport for "
            f"{destination_code}, "
            f"found {len(destination_rows)}"
        )

    destination = destination_rows.iloc[0]

    # Calculating Route Distance
    distance_km = haversine_distance(
        hub["latitude"],
        hub["longitude"],
        destination["latitude"],
        destination["longitude"],
    )

    distance_km = round(distance_km)

    # Calculating Block Hours
    one_way_block_hours = estimate_block_time(distance_km)

    turnaround_hours = turnaround_minutes / 60

    # Calculating Round Trip Block Hours
    round_trip_block_hours = round(
        (2 * one_way_block_hours)
        + (2 * turnaround_hours),
        2,
    )

    # Check Aircraft Range, should expect true so far since every route is in range
    range_feasible = (distance_km <= planning_range_km)

    route_rows.append(
        {
            "route_id": f"{HUB}-{destination_code}",
            "origin": HUB,
            "destination": destination_code,
            "distance_km": distance_km,
            "one_way_block_hours": one_way_block_hours,
            "round_trip_block_hours": round_trip_block_hours,
            "aircraft_type": aircraft_type,
            "range_feasible": range_feasible,
            "frequency_options": "|".join(
                map(str, FREQUENCY_OPTIONS)
            ),
        }
    )

# Adding to Dataframe
routes = pd.DataFrame(route_rows)

# Saving it
routes.to_csv(
    OUTPUT_PATH,
    index=False,
)

print(f"Created {OUTPUT_PATH}")
print(routes.to_string(index=False))
