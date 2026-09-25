import pandas as pd

# Loading Data
ROUTES_PATH = "data/routes.csv"
MARKET_ASSUMPTIONS_PATH = "data/market_assumptions.csv"
OUTPUT_PATH = "data/routes.csv"

routes = pd.read_csv(ROUTES_PATH)

market_assumptions = pd.read_csv(
    MARKET_ASSUMPTIONS_PATH
)

# Merge the dataset
routes = routes.merge(market_assumptions, on="destination", how="left",)

# Safety check
if routes["base_weekly_demand"].isna().any():
    missing = routes.loc[
        routes["base_weekly_demand"].isna(),
        "destination",
    ].tolist()

    raise ValueError(
        f"Missing market assumptions for: {missing}"
    )

# Base Fare
routes["base_fare"] = (45 + 0.065 * routes["distance_km"])

# Average Fare
routes["average_fare"] = (routes["base_fare"] * routes["fare_multiplier"]).round(2)

# Creating Airport Service Cost
AIRPORT_COSTS = {
    "low": 1500,
    "medium": 2000,
    "high": 2800,
}

routes["airport_service_cost_per_rotation"] = (routes["airport_cost_tier"].map(AIRPORT_COSTS))

# Base Assumptions
BASE_ROTATION_COST = 2500
COST_PER_KM = 2.40
COST_PER_BLOCK_HOUR = 850

# Flight Operating Cost
routes["flight_operating_cost_per_rotation"] = (BASE_ROTATION_COST + COST_PER_KM * routes["distance_km"] * 2 + COST_PER_BLOCK_HOUR * routes["round_trip_block_hours"]).round(2)

# Variable Cost
routes["variable_cost_per_rotation"] = (routes["flight_operating_cost_per_rotation"] + routes["airport_service_cost_per_rotation"]).round(2)

routes["weekly_demand"] = (
    routes["base_weekly_demand"]
)

# Remove Base Fare from final dataset
routes = routes.drop(
    columns=[
        "base_fare",
    ]
)

# Saving it
routes.to_csv(
    OUTPUT_PATH,
    index=False,
)

print(f"Updated {OUTPUT_PATH}")
print(routes.to_string(index=False))