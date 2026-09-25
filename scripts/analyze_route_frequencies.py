import pandas as pd

from src.economics import evaluate_route

# Defining Paths
ROUTES_PATH = "data/routes.csv"
OUTPUT_PATH = "outputs/results/route_frequency_analysis.csv"

# Load routes
routes = pd.read_csv(ROUTES_PATH)

destinations = routes["destination"].tolist()
frequencies = [0, 3, 4, 7, 10, 14]


# Evaluate every route/frequency combination
results = []

for destination in destinations:
    for frequency in frequencies:
        result = evaluate_route(
            destination,
            frequency,
        )

        results.append(result)

# Turn results into DataFrame
analysis = pd.DataFrame(results)

analysis.to_csv(
    OUTPUT_PATH,
    index=False,
)

print(analysis.to_string(index=False))

best_by_route = (
    analysis
    .sort_values(
        "contribution",
        ascending=False,
    )
    .groupby("route_id")
    .first()
    .reset_index()
)

print("\nBest frequency by route:")
print(
    best_by_route[
        [
            "route_id",
            "frequency",
            "load_factor",
            "contribution",
            "aircraft_hours",
        ]
    ].to_string(index=False)
)

