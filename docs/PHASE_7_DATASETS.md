# Phase 7: Authoritative Environmental Dataset Layer & Ingestion Pipeline

## 1. Overview & Architecture

Phase 7 establishes a traceable, scientific environmental dataset layer for **Darukaa.Earth Biodiversity Intelligence**. It bridges real-world global Earth observation systems and peer-reviewed spatial databases with the canonical `EnvironmentalState` foundation (Phase 1), spatial context engine (Phase 2), multi-metric reasoning engine (Phases 3 & 5), and Nature Risk Profile diagnostic engine (Phase 6).

```
   Authoritative Earth Observation Sources
 ┌─────────────────────────────────────────────────────────────┐
 │ • ISRIC SoilGrids 250m (Soil pH, SOC, Moisture)             │
 │ • ESA Copernicus WorldCover 10m (Land Cover, Land Use)      │
 │ • GBIF Occurrence & Richness (Species, Habitat Diversity)   │
 │ • WorldClim v2.1 Bioclimatic (Temperature, Precipitation)   │
 │ • Global Forest Watch / Hansen GFC (Deforestation %)        │
 │ • UNEP / SEDAC Global Pollution (Index, PM2.5)              │
 └──────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ Environmental Dataset Adapter Layer                         │
 │  • SoilGridsAdapter                                         │
 │  • CopernicusLandCoverAdapter                               │
 │  • GBIFBiodiversityAdapter                                  │
 │  • WorldClimClimateAdapter                                  │
 │  • GlobalForestWatchAdapter                                 │
 │  • UNEPPollutionAdapter                                     │
 └──────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ End-to-End Data Pipeline (EnvironmentalDataPipeline)        │
 │  1. Coordinate Validation (EPSG:4326 bounding [-90, 90])    │
 │  2. Sanitization & Type Coercion                            │
 │  3. Unit Normalization (pH*10->pH, dg/kg->% SOC, K->°C, etc)│
 │  4. Physical Boundary Checks & Severity Flagging            │
 │  5. Explicit Zero vs. Null Auditing (0.0% != None)          │
 │  6. Variable-Level Provenance & Attribution Tracking        │
 └──────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │ Canonical EnvironmentalState + Audit Report + DB Storage    │
 │  • PointQueryResult / StateEnrichmentResponse               │
 │  • DatasetRegistryModel & IngestedObservationModel (DB)     │
 └─────────────────────────────────────────────────────────────┘
```

---

## 2. Integrated Authoritative Datasets

| Domain | Dataset Name | Organization | Spatial Res. | Temporal Coverage | License | Canonical Variables |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Soil** | ISRIC SoilGrids 250m v2.0 | ISRIC - World Soil Information | 250m | 1950–present | CC BY 4.0 | `soil.ph`, `soil.organic_carbon`, `soil.moisture` |
| **Land** | ESA Copernicus WorldCover 10m | European Space Agency (ESA) | 10m | 2020–present | CC BY 4.0 | `land.land_cover`, `land.land_use` |
| **Biodiversity**| GBIF Species Occurrence & Richness | Global Biodiversity Information Facility | Point / 1km² | 1758–present | CC0 / CC BY 4.0 | `biodiversity.species_richness`, `biodiversity.habitat_diversity` |
| **Climate** | WorldClim v2.1 Bioclimatic | WorldClim / UC Berkeley | 1km (30s) | 1970–2000 climatology | CC BY 4.0 | `climate.temperature`, `climate.rainfall` |
| **Deforestation**| Global Forest Watch (Hansen GFC v1.10)| UMD / Google / USGS / NASA | 30m | 2000–2023 | CC BY 4.0 | `human_impact.deforestation` |
| **Pollution** | UNEP / SEDAC Global Pollution Index | UNEP / Columbia Univ SEDAC | ~1km | 2010–2022 | CC BY 4.0 | `human_impact.pollution` |

---

## 3. Schema & Database Models

### Pydantic Schemas (`backend/app/schemas/dataset.py`)
- `DatasetMetadata`: Authoritative metadata, organization, open-access licensing, DOIs/URLs, raw and canonical units, limitations.
- `DataQualityCheck`: Granular audit check logging `flag_type` (`RANGE_VALID`, `UNIT_CONVERTED`, `OBSERVED_ZERO`, `MISSING_VALUE`, `RANGE_OUT_OF_BOUNDS`, `COORDINATE_OUT_OF_BOUNDS`, `SYNTHETIC_DATA`, `ADAPTER_DEGRADED`), severity (`INFO`, `WARNING`, `ERROR`), original vs transformed values, applied transformation rules.
- `VariableProvenance`: Complete scientific audit trail for each variable (dataset ID, license, raw measurement, canonical harmonized value, spatial and temporal resolutions, known limitations, synthetic indicator).
- `DataQualityReport`: Aggregated summary (total checks, passed, warnings, errors, is_valid, list of missing variables, list of zero variables, synthetic count).
- `PointQueryResult`: Output of querying all 6 adapters for coordinate point.
- `StateEnrichmentRequest` & `StateEnrichmentResponse`: Non-destructive state enrichment preserving user-input metrics while populating missing variables from authoritative sources.

### SQLAlchemy Database Models (`backend/app/models/dataset.py`)
- `DatasetRegistryModel` (`dataset_registry` table): Persistent store of dataset licenses, variables, units, resolutions, citations.
- `IngestedObservationModel` (`ingested_observations` table): Full audit history of ingested raw observation payloads, normalized states, provenance JSON, quality reports, validity flags, and synthetic flags.

---

## 4. Normalization & Validation Process

1. **Coordinate Verification**: Verifies latitude in `[-90.0, 90.0]` and longitude in `[-180.0, 180.0]`.
2. **Unit Conversion**:
   - Soil pH: Detects integer scale (`pH*10` / `pHx10` e.g. 58 → 5.8 pH).
   - Soil Organic Carbon: Converts `dg/kg` (e.g. 240 dg/kg → 2.4% SOC) or `g/kg` (e.g. 35 g/kg → 3.5% SOC) to standard percentage `%`.
   - Temperature: Converts Kelvin (e.g. 298.15 K → 25.0 °C) and tenths of degrees Celsius to standard `°C`.
   - Precipitation: Converts meters (e.g. 1.5 m → 1500.0 mm) to millimeters `mm`.
3. **Physical Boundary Checks**:
   - Soil pH: `[0.0, 14.0]`
   - Soil Organic Carbon: `[0.0, 60.0%]`
   - Soil Moisture: `[0.0, 100.0%]`
   - Species Richness: `[0, 100,000]`
   - Habitat Diversity Index: `[0.0, 100.0]`
   - Temperature: `[-60.0, 65.0°C]`
   - Rainfall: `[0.0, 15,000.0 mm]`
   - Deforestation Loss: `[0.0, 100.0%]`
   - Pollution Index: `[0.0, 100.0]`

---

## 5. Explicit Zero vs. Null Auditing

The system strictly adheres to the scientific imperative that **missing values must never be converted to zero**:
- **Observed Zero (`0.0`, `0`)**: Explicitly audited and flagged with `QualityFlagType.OBSERVED_ZERO` (e.g., 0.0% deforestation detected in satellite baseline, 0 count in core hyper-arid desert transect, 0.0 mm rain in Atacama). Preserved as `0.0`.
- **Missing / Unmeasured (`None`)**: Flagged with `QualityFlagType.MISSING_VALUE`. Preserved as `None` without guessing or defaulting.

---

## 6. Synthetic Data Marking

Synthetic data is permitted solely for unit tests or fallback when explicitly requested via `allow_synthetic_fallback=True`. Any synthetic observation is strictly flagged with `is_synthetic=True` on `RawDatasetObservation`, logged as `SYNTHETIC_DATA` in `DataQualityCheck`, recorded on `VariableProvenance.is_synthetic`, and surfaced in the UI.

---

## 7. API Endpoints (`/api/v1/datasets`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/registry` | List all 6 registered authoritative datasets with licenses and limitations. |
| `GET` | `/registry/{dataset_id}` | Retrieve specific dataset metadata. |
| `POST` | `/query-point` | Query all 6 authoritative datasets for coordinates, returning canonical state, provenance, and quality report. |
| `POST` | `/ingest` | Run raw observation through validation, unit conversion, and database storage. |
| `POST` | `/enrich-state` | Non-destructively enrich an `EnvironmentalState` with authoritative dataset metrics. |

---

## 8. Test Suite Summary

100 passing backend tests across the application test suite:
- `test_authoritative_dataset_registry`: Validates metadata and licensing for all 6 authoritative datasets.
- `test_unit_conversion_soilgrids`: Validates pH*10 to pH, dg/kg to % SOC, g/kg to % SOC.
- `test_unit_conversion_worldclim`: Validates Kelvin to °C and meters to mm.
- `test_observed_zero_vs_missing_distinction`: Validates strict differentiation of 0.0 vs null across deforestation, species richness, and rainfall.
- `test_invalid_coordinates_and_ranges`: Validates rejection of out-of-bounds coordinates and impossible physical values (pH 16, negative species count).
- `test_synthetic_data_explicit_marking`: Validates synthetic data flags across observations, provenance, and quality reports.
- `test_point_query_all_authoritative_datasets`: Validates multi-domain harmonized point queries.
- `test_state_enrichment_preserves_user_values`: Validates non-destructive enrichment preserving user inputs.
- `test_api_endpoints_integration`: Validates all 5 REST API routes.
