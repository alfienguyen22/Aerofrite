# Aerofrite — Airline Network Planning & Route Optimization

## 1. Project Overview

**Aerofrite** is a fictional Brussels-based hybrid European airline.

The purpose of this project is to build an airline network-planning decision-support system that evaluates potential routes from Brussels Airport and determines:

1. Which destinations Aerofrite should serve.
2. How frequently each selected route should operate.
3. How Aerofrite should allocate its limited aircraft capacity across the network.
4. Which combination of routes produces the highest expected weekly contribution/profit.

The project is designed to simulate a simplified version of the type of analysis performed by airline:

- Network Planning teams
- Route Planning teams
- Schedule Planning teams
- Fleet Planning teams
- Network Strategy teams
- Operations Research teams
- Commercial Analytics teams

The first version will prioritize a clear and explainable optimization model rather than attempting to reproduce every operational detail of a real airline.

---

# 2. Airline Profile

## Airline

**Name:** Aerofrite

**Business model:** Hybrid European carrier

Aerofrite combines elements of a low-cost carrier and a traditional network airline.

The airline is assumed to:

- Maintain relatively high aircraft utilization.
- Operate a primarily point-to-point European network.
- Focus heavily on route economics and profitability.
- Serve both leisure and business-oriented destinations.
- Operate from a single primary base.
- Use one aircraft type to simplify fleet operations.

Aerofrite does not operate connecting-passenger itineraries in Version 1.

---

# 3. Hub

Aerofrite's sole operating base is:

**Brussels Airport (BRU)**

All routes in Version 1 originate from or return to Brussels.

Example:

```text
BRU → BCN
BRU → MAD
BRU → LIS
BRU → FCO
BRU → CPH
```

Routes between two non-Brussels airports are outside the scope of Version 1.

---

# 4. Fleet

Aerofrite initially operates:

**5 Airbus A320neo aircraft**

Initial modeling assumptions:

| Attribute | Assumption |
|---|---:|
| Aircraft type | Airbus A320neo |
| Fleet size | 5 |
| Seats per aircraft | 180 |
| Planning range | ~6,300 km |
| Turnaround time | 45 minutes |
| Maximum usable hours per aircraft per day | 11 hours |
| Planning period | 7 days |

These values are initial modeling assumptions and may be refined later.

The entire Version 1 fleet uses the same aircraft type.

This means Aerofrite does not initially need to decide which aircraft type should operate each route.

---

# 5. Geographic Scope

Aerofrite may consider any destination that can reasonably be served nonstop from Brussels using an Airbus A320neo.

Candidate destinations may therefore include airports in:

- Western Europe
- Central Europe
- Eastern Europe
- Scandinavia
- Southern Europe
- Mediterranean destinations
- North Africa
- Selected Middle Eastern destinations where operationally feasible

A candidate route must fall within the modeled operating range of the aircraft.

The initial dataset should contain approximately:

**40–60 candidate destinations**

The first development dataset may contain only 5–10 routes for testing.

---

# 6. Planning Horizon

Aerofrite optimizes its network over a representative:

**One-week planning period**

All demand, revenue, costs, frequencies, and aircraft utilization will therefore initially be expressed on a weekly basis.

Example:

```text
BRU-BCN
7 flights per week
```

means approximately one outbound BRU → BCN service per day.

For modeling simplicity, a "weekly flight frequency" refers to departures from Brussels.

The corresponding return flight to Brussels is assumed to be required as part of the aircraft rotation.

---

# 7. Core Business Question

The primary question AeroPlan should answer is:

> Given Aerofrite's fleet, commercial opportunities, operating costs, and candidate destinations, which routes should the airline operate and how frequently should it fly them in order to maximize expected weekly contribution?

The model should recognize that aircraft are limited resources.

A route may therefore be profitable on its own but still not be selected if another route provides a better use of the same aircraft capacity.

---

# 8. Primary Optimization Objective

The primary objective is:

## Maximize expected weekly network contribution

Conceptually:

```text
Network Contribution
=
Passenger Revenue
-
Variable Flight Operating Costs
-
Airport and Route Operating Costs
-
Fixed Route Operating Costs
```

The optimization should evaluate the network as a whole rather than simply selecting every individually profitable route.

---

# 9. Revenue Model

Passenger revenue will initially be estimated using:

```text
Passenger Revenue
=
Passengers Carried × Average Fare
```

For each route, the model will contain an estimated:

- Weekly passenger demand
- Average one-way fare
- Expected market capture or demand assumption

Commercial figures such as passenger demand and fares will initially be simulated.

They should remain plausible but must not be presented as actual airline proprietary or observed passenger data.

Future versions may incorporate more sophisticated demand and pricing behavior.

---

# 10. Demand Model

Version 1 will use simulated route-level passenger demand.

Example:

```text
BRU → BCN

Estimated weekly demand:
1,500 passengers

Average fare:
€120
```

Passenger numbers carried cannot exceed either:

1. Estimated passenger demand.
2. Available seat capacity.

Therefore:

```text
Passengers Carried
=
min(
    Expected Demand,
    Available Seats
)
```

where:

```text
Available Seats
=
Weekly Frequency × Aircraft Seats
```

Example:

```text
Frequency: 7 flights/week
Seats: 180

Available Seats:
7 × 180 = 1,260
```

If estimated demand is 1,500 passengers, the airline cannot carry more than 1,260 passengers under this simplified model.

---

# 11. Route Frequency Decisions

The optimizer should decide both:

### Route activation

Whether Aerofrite should operate a route at all.

Example:

```text
BRU → BCN = OPEN
BRU → TLL = NOT OPEN
```

### Weekly frequency

If the route is operated, the optimizer should select from a defined set of airline-style frequencies.

Initial allowed frequencies:

```text
0 flights/week
3 flights/week
4 flights/week
7 flights/week
10 flights/week
14 flights/week
```

Where:

```text
0 = route not operated
```

The allowed frequencies may later vary by route.

For example, some routes may only allow:

```text
0
3
7
14
```

while thinner leisure routes might allow:

```text
0
2
3
4
7
```

Version 1 should begin with a common frequency set for simplicity.

---

# 12. Route Cost Structure

A major purpose of the model is to recognize that operating a route involves more than fuel.

Aerofrite's route economics should include several categories of cost.

## 12.1 Variable flight operating costs

These are incurred whenever a flight operates.

Potential components include:

- Fuel
- Flight crew
- Cabin crew
- Maintenance
- Navigation charges
- Landing charges
- Ground handling
- Airport passenger-related charges
- Other flight-dependent operational costs

For the earliest prototype, these components may be combined into:

```text
Estimated Cost Per Flight
```

Later versions should separate these components.

---

# 12.2 Airport service costs

Operating from an airport may involve costs such as:

- Ground handling
- Check-in services
- Gate services
- Baggage handling
- Airport charges
- Security-related charges
- Station support

These may be modeled through a combination of:

```text
cost_per_departure
```

and:

```text
cost_per_passenger
```

depending on the cost.

---

# 12.3 Fixed route operating cost

Opening and maintaining a destination involves costs that may exist even if relatively few flights operate.

Examples might include:

- Station setup
- Local operational support
- Commercial setup
- Contract administration
- Marketing
- Ground-handler agreements
- Ongoing station overhead

Version 1 will represent these through:

```text
weekly_fixed_route_cost
```

The cost is incurred only if Aerofrite operates the route.

Conceptually:

```text
If route is closed:
Fixed route cost = €0

If route is open:
Fixed route cost = specified weekly amount
```

This gives the optimizer a meaningful economic tradeoff when deciding whether to open a destination.

---

# 12.4 Future route-launch costs

True route-launch expenses may be one-time costs rather than recurring weekly costs.

Examples include:

- Initial marketing campaign
- Launch promotion
- Station establishment
- Training
- Initial supplier setup

These will not be modeled separately in Version 1.

A future version may distinguish:

```text
One-Time Route Launch Cost
```

from:

```text
Recurring Weekly Station Cost
```

For Version 1, route-opening economics will be represented primarily using the weekly fixed route operating cost.

---

# 13. Aircraft Time Model

Aircraft availability is one of the main constraints.

Each route consumes aircraft time.

A simplified round-trip rotation should include:

```text
BRU → Destination flight time
+
Destination turnaround
+
Destination → BRU flight time
+
BRU turnaround allowance where appropriate
```

Example:

```text
BRU → BCN        2h 10m
Turnaround          45m
BCN → BRU        2h 15m

Approximate rotation:
5h 10m
```

The exact aircraft-time methodology can be refined during development.

---

# 14. Fleet Capacity Constraint

Aerofrite operates five aircraft.

The optimizer cannot schedule more aircraft hours than the fleet can provide.

Initial theoretical weekly capacity:

```text
5 aircraft
×
11 usable hours/day
×
7 days
=
385 aircraft-hours/week
```

A utilization buffer may later be introduced to account for:

- Maintenance
- Delays
- Schedule recovery
- Aircraft positioning
- Operational resilience

The initial optimizer may use a simplified weekly aircraft-hours limit.

---

# 15. Aircraft Range Constraint

A route may only be operated if it falls within the modeled operating capability of the Airbus A320neo.

Conceptually:

```text
Route Distance <= Allowed Aircraft Range
```

Version 1 does not need to model detailed real-world range effects such as:

- Payload-range tradeoffs
- Weather
- Headwinds
- Runway length
- Airport elevation
- Alternate fuel
- Aircraft configuration differences

These may be introduced in future versions.

---

# 16. Capacity Constraint

Passengers carried cannot exceed available seats.

For route `r`:

```text
Seat Capacity
=
Frequency × 180
```

Passenger volume must satisfy:

```text
Passengers Carried <= Seat Capacity
```

and:

```text
Passengers Carried <= Estimated Demand
```

---

# 17. Route Frequency Constraints

If a route is opened, its selected frequency must come from the allowed frequency set.

Initial frequency choices:

```text
0
3
4
7
10
14
```

The model should therefore not return arbitrary frequencies such as:

```text
11.37 flights/week
```

Route decisions must correspond to realistic integer service patterns.

---

# 18. Decision Variables

The optimization model will primarily make two decisions.

## 18.1 Route activation

For each route:

```text
route_open[r]
```

where:

```text
0 = route not served
1 = route served
```

---

## 18.2 Route frequency

For each route:

```text
frequency[r]
```

selected from the allowed frequency choices.

Example optimizer result:

| Route | Selected Frequency |
|---|---:|
| BRU-BCN | 14 |
| BRU-MAD | 7 |
| BRU-LIS | 7 |
| BRU-CPH | 10 |
| BRU-TLL | 0 |

---

# 19. Optimization Logic

The optimizer should evaluate the financial return associated with different possible frequencies.

For example:

```text
BRU → BCN

3 flights/week
7 flights/week
10 flights/week
14 flights/week
```

Each frequency produces different:

- Seat capacity
- Passenger volume
- Revenue
- Operating cost
- Fixed-route cost impact
- Aircraft-hours requirement
- Contribution

The optimizer should select the combination of routes and frequencies that produces the highest network contribution while satisfying all constraints.

---

# 20. Example Route Evaluation

A simplified route might look like:

```text
Route:
BRU → BCN

Distance:
1,065 km

Weekly demand:
1,500 passengers

Average fare:
€120

Aircraft:
A320neo

Seats:
180

Selected frequency:
7 flights/week
```

Seat capacity:

```text
7 × 180
=
1,260 seats
```

Passengers:

```text
min(1,500, 1,260)
=
1,260
```

Revenue:

```text
1,260 × €120
=
€151,200
```

Suppose:

```text
Flight operating cost:
€8,000 per outbound flight rotation equivalent

Weekly flight cost:
7 × €8,000
=
€56,000

Weekly fixed route cost:
€12,000
```

Then estimated weekly contribution would be:

```text
€151,200
-
€56,000
-
€12,000
=
€83,200
```

These figures are illustrative rather than real airline financial data.

---

# 21. Route Dataset

The primary route dataset should eventually contain approximately 40–60 candidate destinations.

Initial fields may include:

```text
origin
destination
distance_km
outbound_flight_time_hours
weekly_demand
average_fare
cost_per_flight
weekly_fixed_route_cost
min_frequency
max_frequency
```

Later versions may add:

```text
airport_fee
landing_fee
handling_cost
passenger_fee
competitors
competitor_frequency
market_share
seasonality
business_demand_share
leisure_demand_share
```

---

# 22. Airport Dataset

Real airport information should be used where practical.

Potential fields:

```text
iata
icao
airport_name
city
country
latitude
longitude
```

Latitude and longitude will later support route-map visualization.

---

# 23. Aircraft Dataset

Initial aircraft data:

```text
aircraft_type
seats
planning_range_km
turnaround_minutes
usable_hours_per_day
```

Initial values:

```text
A320neo
180 seats
~6,300 km planning range
45-minute turnaround
11 usable aircraft-hours/day
```

Additional aircraft-cost characteristics may be added later.

---

# 24. Data Philosophy

Aerofrite will use a mixture of real and simulated data.

## Real data

Where practical, use real values for:

- Airport locations
- Airport codes
- Airport coordinates
- Approximate airport-to-airport distances
- Aircraft specifications

## Simulated data

Initially simulate:

- Passenger demand
- Average fares
- Market share
- Route profitability
- Airport commercial costs where reliable data is unavailable
- Route-opening costs

Simulated values should be plausible and clearly identified as modeling assumptions.

The project should never imply that simulated commercial data represents actual confidential airline data.

---

# 25. Version 1 Constraints

The first optimization model should include:

### Included

- Fleet size
- Aircraft available hours
- Aircraft seating capacity
- Aircraft range
- Passenger demand
- Allowed route frequencies
- Per-flight operating costs
- Airport/service costs
- Fixed route operating costs

### Not yet included

The following should deliberately be excluded from Version 1:

- Airport slot constraints
- Detailed airport opening hours
- Crew rostering
- Crew duty limits
- Aircraft tail assignment
- Maintenance routing
- Connecting passengers
- Multi-hub operations
- Multiple aircraft types
- Dynamic ticket pricing
- Revenue management
- Fare classes
- Cargo
- Codeshares
- Alliances
- Disruption recovery
- Detailed airport curfews
- Competitor-response modeling

These are potential future extensions.

---

# 26. Connecting Passengers

Version 1 assumes passengers travel directly between Brussels and their destination.

Example:

```text
BRU → MAD
```

The model will not initially consider itineraries such as:

```text
MAD → BRU → CPH
```

Therefore, each route is evaluated primarily as an origin-and-destination market.

Network connectivity may become a Version 2 feature.

---

# 27. Competition

Detailed competition modeling is outside the initial optimization model.

Version 1 passenger demand may implicitly reflect the level of competition through the simulated demand assumptions.

A future version may explicitly include:

```text
number_of_competitors
competitor_frequency
competitor_capacity
estimated_market_share
```

This could allow service frequency and competition to influence Aerofrite's expected demand.

---

# 28. Airport Slots

Airport slot restrictions will not be included in Version 1.

The initial project assumes that Aerofrite can obtain the necessary departure and arrival capacity for any selected route.

Slot constraints may later become an important extension for constrained airports.

---

# 29. Optimization Technology

The initial technology stack will be:

**Programming language**

```text
Python
```

**Data manipulation**

```text
pandas
```

**Optimization**

```text
Google OR-Tools
```

**Application interface**

```text
Streamlit
```

**Visualization**

An interactive mapping library will be selected later for displaying the Aerofrite network.

---

# 30. Planned Application Architecture

The planned project structure is:

```text
aerofrite/
│
├── README.md
├── PROJECT_SPEC.md
├── requirements.txt
├── .gitignore
│
├── app.py
│
├── data/
│   ├── airports.csv
│   ├── aircraft.csv
│   └── routes.csv
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── economics.py
│   ├── optimizer.py
│   ├── scenarios.py
│   └── utils.py
│
├── tests/
│   ├── __init__.py
│   ├── test_economics.py
│   └── test_optimizer.py
│
└── outputs/
    ├── results/
    └── figures/
```

This architecture may evolve as development progresses.

---

# 31. Planned Optimization Output

The optimizer should eventually produce a table similar to:

| Route | Flights / Week | Passengers | Load Factor | Revenue | Cost | Contribution | Aircraft Hours |
|---|---:|---:|---:|---:|---:|---:|---:|
| BRU-BCN | 14 | 2,250 | 89% | €285,000 | €171,000 | €114,000 | 72 |
| BRU-MAD | 7 | 1,090 | 87% | €163,500 | €104,000 | €59,500 | 39 |
| BRU-LIS | 7 | 950 | 75% | €161,500 | €116,000 | €45,500 | 46 |
| BRU-TLL | 0 | 0 | — | €0 | €0 | €0 | 0 |

The exact calculations will be developed incrementally.

---

# 32. Network-Level Outputs

Aerofrite should eventually report:

- Total weekly contribution
- Total weekly revenue
- Total operating cost
- Number of destinations served
- Number of weekly flights
- Expected weekly passengers
- Average network load factor
- Fleet utilization
- Total aircraft-hours used
- Remaining fleet capacity

Example:

```text
Aerofrite Optimized Network

Destinations Served:      21
Weekly Departures:        182
Passengers:               27,430
Average Load Factor:      84.2%
Weekly Revenue:           €3.91M
Weekly Contribution:      €1.14M
Fleet Utilization:        91.3%
```

---

# 33. Scenario Analysis

Once the base optimizer is functional, Aerofrite should support scenario analysis.

Potential scenarios include:

### Base Case

```text
Fleet: 5 aircraft
Normal demand
Normal costs
```

### Higher Fuel Costs

```text
Fuel / flight cost +20%
```

### Demand Shock

```text
Passenger demand -15%
```

### Fleet Expansion

```text
Fleet: 6 aircraft
```

### Fleet Reduction

```text
Fleet: 4 aircraft
```

Scenario comparison should demonstrate how network decisions change when operating conditions change.

---

# 34. Example Strategic Question

One portfolio case study may examine:

> Should Aerofrite lease a sixth Airbus A320neo?

The model would compare:

```text
5-aircraft optimized network
```

against:

```text
6-aircraft optimized network
```

and calculate:

- Additional destinations
- Additional frequencies
- Incremental passengers
- Incremental revenue
- Incremental operating costs
- Incremental network contribution
- Aircraft utilization

This would demonstrate how optimization can support an airline fleet and network-planning decision.

---

# 35. User Interface Vision

The future Streamlit application should contain an interface similar to:

```text
AEROFRITE
Network Planning Simulator

Hub
Brussels (BRU)

Fleet
A320neo: 5

Demand Scenario
Base

Cost Scenario
Base

Minimum Frequency
3 weekly

[ OPTIMIZE NETWORK ]
```

Results should then display:

```text
Network Contribution
€X.XXM / week

Destinations
XX

Passengers
XX,XXX

Fleet Utilization
XX%
```

along with:

- Route table
- Network map
- Route profitability information
- Scenario comparisons

---

# 36. Development Philosophy

Aerofrite should be developed incrementally.

The intended development order is:

```text
1. Define assumptions
        ↓
2. Create route data
        ↓
3. Build route economics calculator
        ↓
4. Validate individual route calculations
        ↓
5. Build small optimization model
        ↓
6. Validate optimizer manually
        ↓
7. Expand to full route network
        ↓
8. Add scenarios
        ↓
9. Build Streamlit interface
        ↓
10. Add network visualization
        ↓
11. Refine commercial assumptions
        ↓
12. Produce portfolio case study
```

Optimization complexity should only increase after simpler versions have been validated.

---

# 37. Validation Principles

Because much of the project may be developed with AI-assisted coding, model validation is essential.

The following principles should be followed:

1. Test route economics independently before introducing optimization.
2. Begin optimization with a very small dataset.
3. Create scenarios where the expected optimal solution can be calculated manually.
4. Verify that passengers never exceed available seats.
5. Verify that passengers never exceed modeled demand.
6. Verify that total aircraft-hours never exceed available fleet capacity.
7. Verify that closed routes incur no route operating cost.
8. Verify that open routes incur the appropriate fixed cost.
9. Verify that only allowed frequencies can be selected.
10. Verify that infeasible routes cannot be selected.
11. Test extreme scenarios such as very high costs or very low demand.
12. Maintain automated tests as the model becomes more complicated.

The goal is not simply to produce an answer from an optimizer, but to understand why the optimizer selected that answer.

---

# 38. Version 1 Success Criteria

Aerofrite Version 1 will be considered successful when the application can:

1. Load approximately 40–60 candidate routes from Brussels.
2. Calculate route economics for different weekly frequencies.
3. Account for both variable and fixed route costs.
4. Determine whether each route should be operated.
5. Select an allowed weekly frequency for each operated route.
6. Respect the capacity of a five-aircraft A320neo fleet.
7. Respect passenger-demand constraints.
8. Respect aircraft-range constraints.
9. Produce an optimized network that maximizes expected weekly contribution.
10. Explain the financial and operational characteristics of the selected routes.
11. Compare alternative commercial or fleet scenarios.
12. Present results through a simple interactive dashboard.

---

# 39. Future Development Ideas

Potential Aerofrite Version 2 and Version 3 features include:

### Commercial modeling

- Competitor frequencies
- Market-share estimation
- Frequency-sensitive demand
- Seasonal demand
- Business vs leisure demand
- Fare elasticity
- Dynamic fares
- Connecting passengers

### Network planning

- Multiple hubs
- Bank structures
- Connection quality
- Route cannibalization
- Network contribution vs local route contribution

### Fleet planning

- Multiple aircraft types
- Aircraft assignment
- Fleet acquisition
- Leasing decisions
- Fleet retirement
- Payload-range limitations

### Schedule planning

- Departure times
- Aircraft rotations
- Tail assignment
- Airport slots
- Airport curfews
- Minimum connection times

### Operations

- Maintenance requirements
- Schedule resilience
- Delay buffers
- Disruption recovery
- Aircraft swaps

### Advanced optimization

- Mixed-integer programming
- Multi-objective optimization
- Robust optimization
- Stochastic demand
- Scenario-based optimization

---

# 40. Core Project Principle

Aerofrite is not intended to answer:

> "Which individual routes appear profitable?"

Instead, it should answer:

> "Given limited aircraft, commercial opportunities, route costs, and operational constraints, what is the best overall network Aerofrite can operate?"

That distinction is the central idea of the project.

A route can be profitable but still be excluded if the aircraft required to operate it generates more value elsewhere.

Aerofrite is therefore fundamentally a **constrained resource-allocation and airline network-planning problem**.