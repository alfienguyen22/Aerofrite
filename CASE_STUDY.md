# Aerofrite Network Planning Case Study

## Executive Summary

Aerofrite is a fictional Brussels-based airline used to explore
airline network planning and fleet-allocation decisions.

This case study asks:

> How should a Brussels-based airline deploy a five-aircraft
> Airbus A320neo fleet across changing seasonal demand while
> preserving operational flexibility?

The model optimizes weekly route frequencies across a candidate
European network while accounting for aircraft-hour capacity,
route economics, frequency-sensitive demand, competition,
seasonality, and operational reserve.

Under the modeled assumptions, the optimized network changes
substantially between winter and summer even though fleet size
and planning capacity remain fixed.

With five aircraft and a 10% operational reserve:

- Winter serves 10 destinations and carries 12,691 passengers.
- Shoulder season serves 13 destinations and carries 13,960 passengers.
- Summer serves 14 destinations and carries 16,540 passengers.
- Modeled weekly contribution rises from approximately €705,000
  in winter to €1.20 million in summer.

The case study illustrates how limited aircraft capacity can be
reallocated as market conditions change, and how operational
resilience creates a measurable commercial tradeoff.


## 1. Planning Problem

Aerofrite operates from Brussels Airport (BRU) with a fictional
fleet of five Airbus A320neo aircraft.

The network planner must determine:

1. Which candidate destinations should be served.
2. How many weekly round trips should operate on each route.
3. How scarce aircraft hours should be allocated across competing markets.

The optimization objective is to maximize modeled weekly network
contribution subject to available fleet capacity.

Contribution is used as a planning metric rather than as a claim
of true airline profit.


## 2. Core Assumptions

The case-study scenario uses:

- Hub: Brussels Airport (BRU)
- Fleet: 5 Airbus A320neo aircraft
- Seats per aircraft: 180
- Usable aircraft time: 11 hours per aircraft per day
- Operational reserve: 10%
- Planning horizon: one week
- Frequency options: 0, 3, 4, 7, 10, or 14 weekly round trips
- Seasons: winter, shoulder, and summer

Five aircraft provide 385 theoretical aircraft-hours per week.

With a 10% operational reserve:

- 38.5 hours are reserved
- 346.5 hours remain available for scheduled flying

The reserve is intended to represent simplified capacity for
maintenance, disruption recovery, and operational flexibility.


## 3. Demand Model

Aerofrite begins with a modeled base weekly demand for each market.

Demand is then adjusted through three stages:

Base Market Demand

→ Seasonal Adjustment

→ Competition Adjustment

→ Frequency Response

→ Effective Demand

→ Available Seat Capacity

→ Passengers Carried

Seasonality differs by market type. Leisure markets receive a
larger modeled summer uplift, while business markets are less
summer-sensitive.

Competition reduces the share of underlying market demand
available to Aerofrite.

Frequency sensitivity reflects the assumption that passengers,
particularly in business markets, value more frequent service.

These factors are transparent modeling assumptions rather than
empirically calibrated demand forecasts.


## 4. Seasonal Network Results

Using the same five-aircraft fleet and 10% operational reserve:

| Season | Destinations | Passengers | Weekly Contribution | Scheduled Hours |
| --- | ---: | ---: | ---: | ---: |
| Winter | 10 | 12,691 | €705,014 | 346.4 |
| Shoulder | 13 | 13,960 | €890,859 | 346.3 |
| Summer | 14 | 16,540 | €1,200,786 | 346.4 |

The optimizer uses almost all available planning capacity in
each season, but the route mix changes substantially.


## 5. Winter-to-Summer Reallocation

Between winter and summer:

- Passenger volume increases by 3,849, or approximately 30.3%.
- Modeled weekly contribution increases by approximately €495,772,
  or 70.3%.
- The number of served destinations increases from 10 to 14.

Several routes enter the summer network:

- BRU-NAP
- BRU-NCE
- BRU-OPO
- BRU-PMI
- BRU-RAK
- BRU-SPU
- BRU-VCE

Several winter-selected routes leave:

- BRU-LIS
- BRU-MUC
- BRU-WAW

Other frequencies are adjusted:

- BRU-AGP increases from 3 to 4 weekly round trips.
- BRU-FCO decreases from 7 to 4 weekly round trips.

Under the model's seasonal assumptions, summer demand makes a
larger set of leisure-oriented markets attractive enough to
compete successfully for limited aircraft capacity.

The result is not simply an expansion of the winter network.
The optimizer actively reallocates aircraft hours between markets.


## 6. Operational Resilience Tradeoff

The shoulder-season network was also evaluated with and without
an operational reserve.

| Scenario | Destinations | Passengers | Weekly Contribution | Planning Capacity |
| --- | ---: | ---: | ---: | ---: |
| 0% Reserve | 14 | 15,464 | €965,995 | 385.0 h |
| 10% Reserve | 13 | 13,960 | €890,859 | 346.5 h |

Introducing a 10% operational reserve:

- reserves 38.5 aircraft-hours
- reduces modeled passenger volume by 1,504, or about 9.7%
- reduces modeled weekly contribution by approximately €75,136,
  or about 7.8%
- reduces the optimized network by one destination

This represents the modeled opportunity cost of preserving
additional operational flexibility.


## 7. Planning Interpretation

The case study highlights several network-planning principles.

### Aircraft capacity has an opportunity cost

Each route competes for the same limited pool of aircraft hours.
A route may be profitable when evaluated independently but still
remain closed if another use of the aircraft produces greater
network contribution.

### Seasonal planning requires network re-optimization

Changing demand conditions do not simply increase or decrease
passenger totals.

They can alter which destinations are served and which frequencies
are most attractive.

### Fleet utilization alone does not determine network quality

The optimized winter, shoulder, and summer networks all use nearly
100% of planning capacity, but they generate very different
passenger and contribution outcomes.

The allocation of those hours matters as much as the number of
hours used.

### Operational resilience has measurable commercial cost

Holding capacity in reserve reduces the amount available for
scheduled flying.

The Aerofrite model makes this tradeoff explicit rather than
assuming every theoretical fleet hour should be scheduled.


## 8. Limitations

Aerofrite is a strategic network-planning model rather than a
complete airline scheduling system.

The current version does not explicitly model:

- individual aircraft tail assignments
- crew scheduling
- airport slot constraints
- maintenance events
- connecting passengers
- detailed departure times
- day-of-week demand
- aircraft swaps or recovery operations
- real competitor schedules
- empirically calibrated fare or demand forecasts

Commercial assumptions are simplified and should be interpreted
as scenario inputs rather than predictions of actual airline
performance.


## 9. Conclusion

Aerofrite demonstrates how mathematical optimization can combine
commercial demand assumptions with limited aircraft capacity to
support airline network-planning decisions.

In the five-aircraft case study, seasonal demand changes produce
a substantial reallocation of the Brussels network. Summer demand
supports a broader leisure-oriented network and produces higher
modeled passenger volume and contribution, while maintaining the
same fleet and planning capacity.

The operational-reserve analysis also demonstrates that maximizing
scheduled flying is not the only planning objective. Reserving
capacity creates a measurable commercial cost but provides
additional operational flexibility.

Together, these results illustrate the central planning challenge:
allocate scarce fleet capacity to the set of routes and frequencies
that best support the airline's commercial and operational goals.