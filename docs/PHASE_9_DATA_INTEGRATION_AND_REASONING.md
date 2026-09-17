# Phase 9: Data Integration and Ecological Reasoning Pipeline

## Overview

Phase 9 completes the integration between real-world environmental data, authoritative datasets, deterministic multi-metric ecological reasoning, conflict/uncertainty analysis, and the Scientific RAG evidence retrieval system.

The pipeline transforms:
**User Input (NL text / State / Coordinates) + Structured Data + Geographic Context → Harmonized EnvironmentalState → Multi-Metric Deterministic Reasoning (3+ variables) → Targeted Scientific RAG Retrieval → Structured Ecological Findings**

---

## Architecture & Components

### 1. Natural Language & Parameter Extractor (`backend/app/knowledge/text_extractor.py`)
- Extracts numeric metrics (`soil.ph`, `soil.organic_carbon`, `soil.moisture`, `climate.temperature`, `climate.rainfall`, `biodiversity.species_richness`, `biodiversity.habitat_diversity`, `human_impact.deforestation`, `human_impact.pollution`) using precompiled regex patterns.
- Semantic mapping for categorical attributes (`land.land_use`, `land.land_cover`, `spatial_context.region`, `spatial_context.ecosystem`).
- Coordinates extraction `(lat, lon)`.

### 2. Conflict & Uncertainty Detection Engine (`backend/app/knowledge/conflict_detector.py`)
- **User vs Dataset Discrepancies**: Flags significant numerical deviations (e.g. pH delta > 1.5, temperature delta > 8°C, relative percent difference > 40%) as `USER_DATASET_DISCREPANCY` while preserving user-measured on-site data with an uncertainty flag.
- **Geographic / Biome Mismatches**: Flags impossible biome combinations (e.g. polar coordinates with tropical forest claim, hyper-arid coordinates with wetland claim) as `GEOGRAPHIC_MISMATCH`.
- **Temporal Staleness**: Detects historical climatology baselines (e.g. 1970–2000) in high deforestation areas as `TEMPORAL_OUTDATED`.
- **Confidence Penalty**: Quantifies calibrated uncertainty penalties (0.0 to 0.50) applied to downstream findings.

### 3. End-to-End Pipeline Service (`backend/app/knowledge/pipeline_service.py`)
- Orchestrates the full lifecycle:
  1. Parse natural language description & merge with input `EnvironmentalState`.
  2. Resolve spatial context via `GeoContextProvider`.
  3. Enrich state using `EnvironmentalDatasetManager` across authoritative adapters (SoilGrids, WorldClim, Copernicus, GBIF, GFW, UNEP).
  4. Track provenance for every variable (`user_supplied` vs `dataset_derived` vs `unknown`).
  5. Audit for conflicts and compute uncertainty penalty.
  6. Execute multi-metric reasoning across 3+ variables.
  7. Retrieve compact (5–8 chunk) evidence packets from Scientific RAG.
  8. Return structured findings with causal chains, mechanisms, and provenance.

### 4. API Surface (`backend/app/api/v1/endpoints/reasoning.py`)
- `POST /api/v1/reasoning/ecological-findings`: Comprehensive end-to-end endpoint accepting `EcologicalFindingsRequest` and returning `EcologicalFindingsResponse`.
- `POST /api/v1/reasoning/extract-state`: Helper endpoint to parse environmental text into structured parameters.

### 5. Frontend Interactive Interface (`src/components/EcologicalFindingsPipelineView.tsx`)
- Site notes text area with preloaded field scenarios (Western Ghats, Serengeti, Amazon Border, Fennoscandia Peatland).
- Metrics summary bar (User Observed, Dataset Derived, Unknown, Total Findings, Mean Confidence).
- Visual Conflict Reports banner showing exact deltas and applied penalties.
- Detailed Finding cards with domain, severity, contributing metrics with source tags, biophysical mechanism explanations, step-by-step causal chains, and grounded scientific citations.
- Enriched state synchronization button to update global application state.

---

## Verification & Test Results

- **All 126 backend tests passed** in `backend/tests/`.
- Frontend TypeScript linter (`tsc --noEmit`) completed with **zero errors**.
- Vite production build verified with `compile_applet`.

---

## Next Steps (Phases 10+)
- Phase 10: Intervention Engine & Restoration Action Prioritization.
- Phase 11: Feasibility Checking & Biophysical Constraint Validation.
- Phase 12: Ecological Trade-Off Analysis & Multi-Criteria Decision Support.
