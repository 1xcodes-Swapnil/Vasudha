# Canonical Environmental State Specification (Phase 1)

## Overview

The **Canonical Environmental State** represents the verified, multi-dimensional ecological foundation of Darukaa.Earth. It serves as the single source of truth for all downstream intelligence layers: multi-metric ecological reasoning, Nature Risk profiling, intervention generation, and evidence mapping.

Under our core architectural rule:
> **The Large Language Model is NOT the scientific source of truth.**

Every ecological variable is strictly typed, bounded by physical and ecological realities, and validated prior to reasoning.

---

## State Hierarchy

```
EnvironmentalState
├── soil
│   ├── ph                (0.0 - 14.0 scale; terrestrial soils 2.5 - 11.0)
│   ├── organic_carbon    (0.0 - 100.0 wt % of dry soil mass)
│   └── moisture          (0.0 - 100.0 % volumetric/gravimetric water content)
├── land
│   ├── land_use          (classification, e.g., cropland, agroforestry, pasture)
│   └── land_cover        (vegetative/substrate type, e.g., tropical_moist_forest)
├── biodiversity
│   ├── species_richness  (non-negative integer; count of observed taxa)
│   └── habitat_diversity (0.0 - 100.0 diversity index / structural score)
├── climate
│   ├── temperature       (-90.0°C to 60.0°C ambient / mean annual temperature)
│   └── rainfall          (0.0 to 20,000.0 mm/year mean annual precipitation)
├── human_impact
│   ├── pollution         (numeric 0.0 - 100.0 index or categorical severity)
│   └── deforestation     (0.0 - 100.0 % canopy loss relative to baseline)
└── spatial_context
    ├── latitude          (-90.0 to 90.0 decimal degrees)
    ├── longitude         (-180.0 to 180.0 decimal degrees)
    ├── region            (administrative / geographic territory name)
    └── ecosystem         (ecoregion / biome / habitat classification)
```

---

## Scientific Principles & Validation Rules

### 1. Null vs. Zero Distinction
A critical rule in ecological data modeling is distinguishing missing measurements from observed zero values:
- **`null` / `None`**: Variable is unmeasured, unknown, or omitted.
- **`0` / `0.0`**: Metric was measured and explicitly observed to be zero (e.g., completely desiccated soil moisture = `0.0%`, zero species observed = `0`, zero rainfall = `0.0 mm`, zero detected pollution = `0.0`).

### 2. State Update & Non-Destructive Merge Semantics
When updating an existing profile across conversational turns or successive surveys:
- **Rule 1**: Latest explicit values override previously stored values.
- **Rule 2**: Missing fields or `null` in an update payload do **NOT** erase previously known values.
- **Rule 3**: An explicit `0` or `0.0` **DOES** override an older non-zero value.

### 3. Physical & Scientific Bounds
- **Soil pH**: Enforced between `0.0` and `14.0`. Extreme natural soils range between 2.5 (pyritic acid sulfate) and 10.5 (hyper-alkaline sodic).
- **Rainfall**: Strictly non-negative (`>= 0.0 mm`). Capped at `20,000.0 mm` (surpassing earth records in Cherrapunji).
- **Soil Organic Carbon & Moisture**: Enforced between `0.0%` and `100.0%`.
- **Coordinates**: Latitude `[-90.0, 90.0]`, Longitude `[-180.0, 180.0]`. Boundary values are preserved with 6 decimal place precision.
- **Strict Schema**: `extra = "forbid"` blocks arbitrary hallucinatory keys from polluting the state.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/environmental-state` | Create persistent profile with canonical state |
| `GET` | `/api/v1/environmental-state/{id}` | Retrieve profile by UUID |
| `PATCH` | `/api/v1/environmental-state/{id}` | Partial non-destructive update with merge rules |
| `GET` | `/api/v1/environmental-state` | List recent profiles |
| `POST` | `/api/v1/environmental-state/validate` | Pure stateless schema validator |

---

## Verification Test Matrix

The test suite in `backend/tests/test_environmental_state.py` validates:
1. Complete state validation (15 metrics)
2. Partial states with sparse data
3. Null vs. Zero semantics & non-destructive preservation
4. Invalid pH rejection (< 0.0, > 14.0)
5. Invalid rainfall rejection (< 0.0, > 20,000.0 mm)
6. Invalid coordinates rejection (lat outside [-90, 90], lon outside [-180, 180])
7. Exact boundary coordinate values (-90, 90, -180, 180, 0, 0)
8. State update merge behavior
9. Conflicting values (latest explicit override)
10. Default initialization with missing fields
11. Extra field prohibition (`extra='forbid'`)
12. Malformed JSON and type coercion rejections
13. API create, retrieve, patch, and validation endpoints
