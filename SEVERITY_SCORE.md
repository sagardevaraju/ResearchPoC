# Shipment Impact Severity Score - Mathematical Formulation

## Overview

The shipment impact severity score is a quantitative measure that assesses the risk and potential disruption to individual shipments based on multiple factors. The score ranges from 0 to 1, where higher values indicate more severe impact.

## Mathematical Formula

```
Impact_Score = w₁ × Geopolitical_Severity + w₂ × Delay_Factor + w₃ × Performance_Factor + w₄ × Route_Risk
```

### Weight Coefficients

The weights are calibrated to reflect the relative importance of each factor:

- **w₁ = 0.4** (Geopolitical Severity)
- **w₂ = 0.3** (Delay Factor)
- **w₃ = 0.2** (Performance Factor)
- **w₄ = 0.1** (Route Risk)

Sum: w₁ + w₂ + w₃ + w₄ = 1.0

## Component Calculations

### 1. Geopolitical Severity (G)

**Range:** [0, 1]

**Source:** Derived from geopolitical news analysis and scenario severity ratings.

**Calculation:**
```
G = min(max(scenario_severity, 0.0), 1.0)
```

**Examples:**
- Trade embargo: 0.95
- Trade block: 0.9
- Tariff increase: 0.8
- Sanctions: 0.9
- Port disruption: 0.7

### 2. Delay Factor (D)

**Range:** [0, 1]

**Formula:**
```
D = min(delay_days / lead_time, 1.0)

where:
  delay_days = max((actual_ETA - planned_ETA).days, 0)
  lead_time = supplier_lead_time_days (default: 30)
```

**Examples:**
- 5-day delay with 30-day lead time: D = 5/30 = 0.167
- 15-day delay with 25-day lead time: D = 15/25 = 0.6
- 40-day delay with 30-day lead time: D = 1.0 (capped)

### 3. Performance Factor (P)

**Range:** [0, 1]

**Formula:**
```
P = 1.0 - performance_score

where:
  performance_score = (supplier_performance + on_time_rate) / 2
```

**Interpretation:**
- Higher supplier performance = Lower performance factor (less risk)
- Poor historical performance = Higher performance factor (more risk)

**Examples:**
- Supplier score: 0.9, On-time rate: 0.95 → P = 1.0 - 0.925 = 0.075
- Supplier score: 0.6, On-time rate: 0.7 → P = 1.0 - 0.65 = 0.35

### 4. Route Risk Factor (R)

**Range:** [0, 1]

**Formula:**
```
R = min(origin_risk + destination_risk + distance_complexity, 1.0)

where:
  origin_risk = 0.5 if origin in high_risk_ports else 0.0
  destination_risk = 0.3 if destination in high_risk_ports else 0.0
  distance_complexity = 0.2 for Trans-Pacific routes else 0.0
```

**High-Risk Ports:**
- Shanghai, Shenzhen, Hong Kong (China)
- Suez Canal, Port Said (Egypt)
- Aden (Yemen)
- Red Sea region

**Examples:**
- Shanghai → Los Angeles: R = 0.5 + 0.0 + 0.2 = 0.7
- Ho Chi Minh → Oakland: R = 0.0 + 0.0 + 0.0 = 0.0
- Hong Kong → Dubai: R = 0.5 + 0.0 + 0.0 = 0.5

## Complete Example Calculation

### Scenario: China Trade Block Impact on Electronics Shipment

**Given:**
- Geopolitical severity: 0.9 (Trade block)
- Planned ETA: 2025-02-18
- Actual ETA: 2025-02-23 (5 days delay)
- Supplier lead time: 30 days
- Supplier performance score: 0.85
- On-time rate: 0.80
- Origin: Shanghai
- Destination: Los Angeles

**Calculations:**

1. **Geopolitical Severity:**
   ```
   G = 0.9
   ```

2. **Delay Factor:**
   ```
   delay_days = 5
   D = 5 / 30 = 0.167
   ```

3. **Performance Factor:**
   ```
   performance_score = (0.85 + 0.80) / 2 = 0.825
   P = 1.0 - 0.825 = 0.175
   ```

4. **Route Risk:**
   ```
   origin_risk = 0.5 (Shanghai is high-risk)
   destination_risk = 0.0 (Los Angeles is not high-risk)
   distance_complexity = 0.2 (Trans-Pacific)
   R = 0.5 + 0.0 + 0.2 = 0.7
   ```

**Final Impact Score:**
```
Impact_Score = 0.4 × 0.9 + 0.3 × 0.167 + 0.2 × 0.175 + 0.1 × 0.7
             = 0.36 + 0.050 + 0.035 + 0.07
             = 0.515
```

**Interpretation:** Medium-High Impact (0.515/1.0)

## Risk Classification

Based on the final impact score:

| Score Range | Risk Level | Color Code | Action Required |
|-------------|------------|------------|-----------------|
| 0.00 - 0.30 | Low | Green | Monitor |
| 0.30 - 0.50 | Medium | Yellow | Review alternatives |
| 0.50 - 0.70 | High | Orange | Immediate action |
| 0.70 - 1.00 | Critical | Red | Emergency mitigation |

## Use Cases

1. **Prioritization:** Sort alerts by impact score to focus on highest-risk shipments
2. **Resource Allocation:** Allocate expedited shipping or alternative sourcing based on score
3. **Trend Analysis:** Track impact scores over time to identify systemic issues
4. **Scenario Planning:** Model different geopolitical scenarios and their impact

## Limitations and Assumptions

1. **Linear Aggregation:** Assumes factors combine linearly (no exponential effects)
2. **Static Weights:** Weights may need adjustment based on industry or business context
3. **Data Quality:** Score accuracy depends on input data quality
4. **Temporal Factors:** Does not account for time-decay of risks
5. **Binary Port Risk:** Ports are either high-risk or not (no gradation)

## Future Enhancements

1. **Dynamic Weight Adjustment:** Machine learning to optimize weights based on historical outcomes
2. **Non-linear Interactions:** Account for multiplicative effects between factors
3. **Temporal Decay:** Reduce impact of historical delays over time
4. **Multi-modal Risk:** Include air freight, rail, and truck routing
5. **Financial Impact:** Incorporate cost/value of shipment
6. **Cascading Effects:** Model downstream impacts on supply chain
