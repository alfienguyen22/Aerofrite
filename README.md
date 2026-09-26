# Aerofrite ✈️

### Airline Network Planning & Optimization

Aerofrite is an interactive airline network-planning application that models how a fictional Brussels-based carrier could allocate a limited Airbus A320neo fleet across European markets.

The project combines **route economics, demand modeling, fleet-capacity constraints, seasonality, competition, and mathematical optimization** to determine which destinations to serve and how frequently to operate them.

**[🚀 Launch the Live App](https://aerofrite.streamlit.app/)**

> **Note:** Aerofrite is a fictional airline and a portfolio project. Commercial demand, fares, costs, competition, and seasonal effects are modeled assumptions rather than forecasts of actual airline performance.

---

## Overview

Airline network planning involves more than identifying routes with positive standalone economics. Airlines must decide how to allocate scarce aircraft capacity across competing opportunities while considering demand, schedule frequency, seasonality, and operational resilience.

Aerofrite models this problem from a Brussels hub (`BRU`) across **40 candidate European markets**.

For each route, the optimizer chooses one of the following weekly round-trip frequencies:

```text
0, 3, 4, 7, 10, or 14
```

A frequency of `0` means that the route remains closed.

The objective is to select the combination of routes and frequencies that maximizes **modeled weekly network contribution** without exceeding available aircraft capacity.

---

## Live Application

### [Open Aerofrite on Streamlit →](https://aerofrite.streamlit.app/)

The application contains six analysis areas:

| Page | Purpose |
|---|---|
| **Network Overview** | Explore the optimized network, fleet utilization, KPIs, route map, and selected services |
| **Route Analysis** | Inspect individual route economics, demand assumptions, frequency alternatives, and closed-route opportunities |
| **Scenario Analysis** | Compare fleet sizes, seasons, operational reserve levels, and network changes |
| **Demand & Market Model** | Explore frequency-sensitive demand, competition, seasonality, and the resulting demand chain |
| **Case Study** | Follow a fixed five-aircraft seasonal network-planning analysis |
| **Methodology** | Review optimization logic, assumptions, equations, data classification, and limitations |

---

## Key Features

### Network Optimization

Aerofrite uses **Google OR-Tools CP-SAT** to select route-frequency combinations subject to fleet-capacity constraints.

The optimizer evaluates:

- route-level passenger demand
- service frequency
- modeled average fares
- operating costs
- airport cost tiers
- fixed route costs
- seasonal demand
- competitive intensity
- aircraft-hour requirements
- operational reserve capacity

A route can therefore generate positive standalone contribution and still remain closed if another allocation of the same aircraft capacity produces greater network value.

### Frequency-Sensitive Demand

Passenger demand is modeled as responsive to service frequency.

Business-oriented markets are assumed to be more sensitive to low frequencies, while leisure markets retain a larger share of demand at lower service levels.

The demand chain is:

```text
Base Market Demand
        ↓
Seasonality
        ↓
Competition
        ↓
Frequency Response
        ↓
Effective Demand
        ↓
Seat Capacity
        ↓
Passengers Carried
```

### Seasonal Network Planning

The entire network can be re-optimized for:

- Winter
- Shoulder season
- Summer

Different market types receive different modeled seasonal adjustments, allowing aircraft capacity to shift between markets as demand conditions change.

### Operational Resilience

Users can reserve part of the theoretical fleet capacity rather than scheduling every available aircraft hour.

For example:

```text
Theoretical Fleet Capacity
        ↓
Operational Reserve
        ↓
Planning Capacity
        ↓
Optimized Network
```

The application then quantifies the commercial opportunity cost of retaining this spare capacity.

### Interactive Route Analysis

Every candidate route can be inspected independently of whether it appears in the current optimized network.

For each route, Aerofrite displays:

- distance
- market type
- competitive intensity
- base demand
- seasonal adjustment
- competition adjustment
- frequency response
- effective demand
- passengers carried
- load factor
- aircraft hours
- weekly contribution
- contribution per aircraft hour

Alternative frequency options can also be compared directly.

---

## Portfolio Case Study

Aerofrite includes a fixed case study using:

```text
Hub:                 Brussels (BRU)
Fleet:               5 Airbus A320neo aircraft
Seats:               180 per aircraft
Operational Reserve: 10%
Planning Capacity:    346.5 aircraft-hours / week
```

### Seasonal Results

| Season | Destinations | Weekly Passengers | Modeled Weekly Contribution |
|---|---:|---:|---:|
| Winter | 10 | 12,691 | €705,014 |
| Shoulder | 13 | 13,960 | €890,859 |
| Summer | 14 | 16,540 | €1,200,786 |

Under the modeled assumptions, moving from the winter to summer network results in approximately:

- **+30.3% weekly passengers**
- **+70.3% modeled weekly contribution**
- **+4 destinations**

Importantly, the summer result is not simply the winter network with more demand. The optimizer reallocates aircraft capacity between routes as their relative economics change.

### Cost of Operational Resilience

For the shoulder-season case:

```text
0% reserve → 385.0 planning hours
10% reserve → 346.5 planning hours
```

Reserving 10% of theoretical capacity removes **38.5 aircraft-hours** from the planning pool.

Under the modeled assumptions, this changes the optimized network by approximately:

- **−1,504 weekly passengers**
- **−€75,136 weekly contribution**
- **−1 destination**

This makes the opportunity cost of operational resilience explicit rather than treating maximum utilization as the only planning objective.

A longer written analysis is available in [`CASE_STUDY.md`](CASE_STUDY.md).

---

## How the Optimization Works

For each candidate route \(r\) and allowable frequency \(f\), the optimizer determines whether that route-frequency combination should be selected.

### Objective

Maximize total modeled network contribution:

```text
Maximize Σ Route Contribution
```

subject to:

### One Frequency per Route

Each destination receives exactly one frequency decision, including the option to remain closed.

### Fleet Capacity

Total scheduled aircraft hours cannot exceed available planning capacity:

```text
Scheduled Aircraft Hours ≤ Planning Capacity
```

Planning capacity is calculated as:

```text
Theoretical Capacity
= Fleet Size × Usable Hours per Aircraft per Day × 7
```

and:

```text
Planning Capacity
= Theoretical Capacity × (1 − Operational Reserve)
```

---

## Route Economics

Aerofrite uses a simplified contribution model rather than accounting profit.

### Revenue

```text
Revenue
= Passengers × Average Fare
```

The modeled fare begins with a distance-based reference:

```text
Reference Fare
= €45 + (€0.065 × Distance in km)
```

A route-specific fare multiplier is then applied.

### Operating Cost

The simplified operating cost per round trip is:

```text
€2,500
+ €2.40 × Round-Trip Distance
+ €850 × Round-Trip Block Hours
+ Airport Cost
```

A weekly fixed route cost is then added.

### Contribution

```text
Weekly Contribution
= Passenger Revenue
− Variable Route Cost
− Weekly Fixed Route Cost
```

**Contribution should not be interpreted as accounting profit, EBIT, operating profit, or net income.**

---

## Demand Model

Aerofrite separates underlying market demand from the demand captured at a particular service frequency.

### Seasonal Adjustment

Different market types respond differently to the modeled season:

| Market Type | Winter | Shoulder | Summer |
|---|---:|---:|---:|
| Business | 100% | 100% | 95% |
| Mixed | 95% | 100% | 110% |
| Leisure | 80% | 100% | 125% |

### Competition Adjustment

| Competition | Demand Multiplier |
|---|---:|
| Low | 100% |
| Medium | 90% |
| High | 80% |

These values are transparent scenario assumptions rather than observed market-share estimates.

### Frequency Response

Aerofrite then applies a market-type-specific frequency multiplier.

For example, at three weekly round trips:

```text
Business market → 30% demand response
Mixed market    → 45%
Leisure market  → 60%
```

At seven weekly frequencies, each market type reaches the model's baseline 100% response.

---

## Technology Stack

| Area | Technology |
|---|---|
| Programming | Python |
| Data processing | pandas, NumPy |
| Optimization | Google OR-Tools CP-SAT |
| Web application | Streamlit |
| Mapping | PyDeck |
| Testing | pytest |
| Version control | Git / GitHub |
| Deployment | Streamlit Community Cloud |

---

## Project Architecture

```text
Aerofrite/
│
├── app.py
│
├── pages/
│   ├── overview.py
│   ├── route_analysis.py
│   ├── scenario_analysis.py
│   ├── demand_model.py
│   ├── case_study.py
│   └── methodology.py
│
├── src/
│   ├── app_state.py
│   ├── app_services.py
│   ├── optimizer.py
│   ├── economics.py
│   ├── demand.py
│   ├── market_adjustments.py
│   ├── scenarios.py
│   ├── case_study.py
│   ├── data_loader.py
│   └── map_utils.py
│
├── data/
├── scripts/
├── tests/
│
├── CASE_STUDY.md
├── PROJECT_SPEC.md
└── requirements.txt
```

The Streamlit pages are kept separate from the underlying analytical logic.

Shared services provide cached access to optimization results and reference data, while the optimization, economics, demand, and scenario logic remain in dedicated modules.

---

## Running Aerofrite Locally

### 1. Clone the repository

```bash
git clone <https://github.com/alfienguyen22/Aerofrite>
cd Aerofrite
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Launch the application

```bash
streamlit run app.py
```

The project was developed using **Python 3.12**.

---

## Testing

The analytical modules are covered by automated tests for areas including:

- route economics
- demand response
- market adjustments
- fleet capacity
- optimizer behavior
- scenario analysis
- operational reserve behavior
- case-study reproducibility
- edge and stress cases

Run the test suite with:

```bash
python -m pytest
```

`pytest` may need to be installed separately if only the production requirements have been installed.

---

## Data & Modeling Approach

Aerofrite deliberately separates reference data from simulated commercial assumptions.

### Reference / Calculated Data

Includes:

- airport codes
- airport names
- airport coordinates
- geographic route distances

Route distances are calculated using the Haversine formula.

### Modeled Project Assumptions

Includes:

- base weekly passenger demand
- market type
- fare multipliers
- competition levels
- airport cost tiers
- route fixed costs
- operating-cost assumptions
- seasonality multipliers
- frequency-demand response

This distinction is important: **Aerofrite is a decision-support model, not a forecast of real airline demand or financial performance.**

---

## Current Scope & Limitations

Aerofrite focuses on **strategic network design and fleet-capacity allocation**.

The current version does not explicitly model:

- individual aircraft tail assignment
- crew scheduling and duty limits
- airport slot constraints
- exact flight departure times
- detailed maintenance scheduling
- connecting passenger flows
- day-of-week demand variation
- disruption recovery
- live competitor schedules
- dynamic ticket pricing
- booking curves
- spill and recapture
- airport curfews
- empirically calibrated demand forecasts

These are intentional simplifications that keep the project focused on route selection, frequency choice, network economics, and scenario analysis.

---

## Potential Extensions

Future versions could extend the optimization toward:

- individual aircraft rotations
- departure-time scheduling
- slot constraints
- connecting passenger flows
- real schedule and fare data
- empirical demand estimation
- fleet-type assignment
- multi-hub network design
- aircraft maintenance constraints
- disruption and recovery optimization

---

## Why I Built This

This project was developed to explore the intersection of:

- airline network planning
- operations research
- mathematical optimization
- commercial analytics
- fleet planning
- decision-support software

It reflects my interest in using optimization and software engineering to solve real operational planning problems, particularly in aviation.

---

## Live Demo

### ✈️ [https://aerofrite.streamlit.app/](https://aerofrite.streamlit.app/)

---

## Disclaimer

Aerofrite is an independent educational and portfolio project built around a fictional airline.

The application is not affiliated with Brussels Airport, Airbus, any airline, or any other aviation organization.

All commercial outputs should be interpreted as results of the project's stated assumptions rather than real-world forecasts or investment, operational, or financial advice.