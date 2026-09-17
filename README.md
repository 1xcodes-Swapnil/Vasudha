# VASUDHA — Biodiversity Intelligence for a Living Earth

> **Hybrid Layered RAG Architecture with Knowledge-Based Ecological Reasoning**
> 
> *Vasudha* (Sanskrit: वसुधा) — The Earth; that which sustains, nourishes, and provides.

VASUDHA is an auditable biodiversity intelligence system engineered to eliminate ecological hallucinations in environmental decision-making. Rather than using large language models as ungrounded sources of truth, VASUDHA implements a strict 13-stage biophysical reasoning pipeline that combines structured ecological knowledge, multi-metric causal reasoning across observed environmental variables, and scientific retrieval grounded in authoritative consensus literature (IPCC, IPBES, FAO, UNEP, CBD).

---

## 1. The Problem: Why Generic LLM Chatbots Fail in Ecology

Generic conversational chatbots and unlayered RAG systems fail when applied to ecological conservation and land management:
1. **Uncalibrated Hallucinations**: Standard models invent quantitative improvements (e.g. claiming "planting trees increases biodiversity by 85% in 6 months" without species or water budget context).
2. **Missing Biophysical Coupling**: They recommend interventions (such as afforestation) without checking critical ecological constraints (e.g., planting high-transpiration trees in semi-arid zones depletes groundwater and causes xylem cavitation).
3. **No Auditable Reasoning Chain**: Generic AI outputs unprovable bullet points without demonstrating the physiological causal flow from observed metrics to targeted ecological pressures.
4. **Lack of Scientific Provenance**: Citations are either fabricated or disconnected from specific quantitative assertions.

---

## 2. The Solution: VASUDHA's Hybrid Layered Architecture

VASUDHA solves these fundamental limitations by decoupling natural language synthesis from scientific truth:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   1. PRESENTATION LAYER (React 19 / TS)                │
│   • Conversational Intelligence UI with cross-turn biophysical memory  │
│   • Canonical Environmental State Inspector & Benchmark Presets        │
│   • Multi-Metric Reasoning & Causal Flow Visualization                 │
│   • "Why this intervention?" Progressive Disclosure & Evidence Audit   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP / JSON API (:3000 -> :8001)
┌───────────────────────────────────▼────────────────────────────────────┐
│                  2. APPLICATION / API LAYER (FastAPI / Node)           │
│   • Strict Pydantic schemas, validation & WMO/FAO range enforcement    │
│   • State-aware conversational synthesis & corpus retrieval endpoints  │
│   • Audited intervention engine with constraint & trade-off scoring   │
└───────────────────┬────────────────────────────────┬───────────────────┘
                    │                                │
┌───────────────────▼────────────────────────────┐   │
│         3. INTELLIGENCE LAYER                  │   │
│   • Multi-Metric Ecological Reasoner (≥3 vars) │   │
│   • Compound Pressure & Synergistic Evaluator  │   │
│   • Feasibility Engine & Claim Validation      │   │
│   • Abstracted LLM Provider (Gemini / others)  │   │
└───────────────────┬────────────────────────────┘   │
                    │                                │
┌───────────────────▼────────────────────────────▼───▼───────────────────┐
│                   4. KNOWLEDGE & RAG LAYER                             │
│   • Tier 1 Scientific Corpus (IPCC, IPBES, FAO, UNEP, CBD)             │
│   • Structured Ecological Baselines & Ontological Relationships        │
│   • High-dimensional semantic embeddings (MiniLM / pgvector)           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                    5. DATA LAYER (PostgreSQL + pgvector)               │
│   • High-dimensional vector index for scientific evidence chunks       │
│   • Authoritative global dataset adapters (SoilGrids, GBIF, WorldClim) │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. The 13-Stage Ecological Pipeline

VASUDHA executes a deterministic, auditable 13-stage pipeline on every evaluation:

1. **Input Ingestion**: Ingests narrative land descriptions, manual sensor metrics, or coordinate queries.
2. **Canonical Environmental State**: Validates biophysical values across Soil (pH, SOC, moisture), Land (use, cover), Biodiversity (richness, habitat score), Climate (rainfall, temperature), and Human Impact (pollution, deforestation).
3. **Geographic & Biome Context**: Resolves spatial coordinates to ecoregion, biome, and elevation baselines.
4. **Multi-Metric Ecological Reasoning**: Cross-evaluates at least 3 environmental variables simultaneously (e.g., Rainfall + SOC + Soil Moisture) to identify compound degradation pressures.
5. **Scientific Corpus Retrieval (RAG)**: Retrieves relevant evidence chunks exclusively from Tier-1 scientific bodies.
6. **Nature Risk Profiling**: Evaluates water stress, soil degradation, habitat fragmentation, and climate risk with explicit uncertainty scores.
7. **Intervention Prescriptions**: Matches identified pressures to context-appropriate interventions.
8. **Feasibility & Ecological Guardrails**: Tests candidate interventions against biophysical thresholds (e.g. soil pH limits, drought tolerance, labor constraints).
9. **Impact Metric Mapping**: Models directional effects (↑ Soil Organic Carbon, ↑ Infiltration, ↓ Thermal Peak Stress) with time horizons.
10. **Scientific Claim Validation**: Audits every quantitative and causal claim against retrieved literature; ungrounded assertions are flagged or excised.
11. **Explainability Engine ("Why this intervention?")**: Generates a 6-step causal chain: Observed Conditions → Ecological Pressure → Mechanism → Intervention → Directional Metric Effect → Literature Consensus.
12. **Context-Specific Trade-offs & Limitations**: Identifies real-world implementation tensions (e.g. water allocation during establishment, light competition).
13. **Audited Response Synthesis**: Delivers structured, transparent recommendations through the conversational and visual interfaces.

---

## 4. Benchmark Demonstration Scenario

VASUDHA includes a built-in benchmark scenario ready for evaluation in one click:

### Scenario: Degraded Semi-Arid Monoculture Cropland
- **Location**: Deccan Plateau, India (12.9716° N, 77.5946° E)
- **Ecosystem**: Tropical Dry Deciduous / Cropland Ecotone
- **Observed Metrics**:
  - Soil Organic Carbon: **0.8%** (Critical depletion; FAO threshold <1.0%)
  - Soil Moisture: **14.0%** (Severe deficit)
  - Soil pH: **5.4** (Moderately acidic)
  - Annual Rainfall: **480 mm** (Semi-arid drought-prone)
  - Mean Temperature: **32.5 °C**
  - Habitat Diversity: **22/100** (Monoculture simplification)
  - Species Richness: **18**
  - Deforestation / Canopy Loss: **14.5%**
- **Compound Pressures**: Hydrological-biophysical coupling failure (rain deficit + low SOC prevents rainfall infiltration, exacerbating surface baking and vegetative drought strain).
- **Prescribed Interventions**:
  1. *Multistrata Agroforestry with Native Leguminous Trees* (Time horizon: 3–5 years | Feasibility: Suitable | High Confidence)
  2. *Mixed Native Cover Cropping & Residue Mulching* (Time horizon: 1–2 seasons | Feasibility: Suitable | High Confidence)
  3. *Perennial Contour Vegetative Buffers & Swales* (Time horizon: 2–3 years | Feasibility: Suitable | High Confidence)

---

## 5. Authoritative Scientific Knowledge Sources

VASUDHA's knowledge corpus strictly adheres to a three-tier evidence hierarchy:

| Source | Organization | Focus / Domain |
| :--- | :--- | :--- |
| **IPCC AR6 WGII (2022)** | Intergovernmental Panel on Climate Change | Chapter 2 (Terrestrial Ecosystems) & Climate-Resilient Land Management |
| **Global Assessment (2019)** | IPBES | Biodiversity Loss Drivers, Ecosystem Restoration & Landscape Corridors |
| **Recarbonizing Global Soils (2022)** | FAO / ITPS | Soil Organic Carbon Sequestration (GSOCseq) & Soil Biodiversity Guidelines |
| **Nature-Based Solutions Synthesis** | UNEP | Ecosystem-based Adaptation & Watershed Rehabilitation Standards |
| **Kunming-Montreal Framework (2022)** | CBD | Target 2 & 10 (Restoration of degraded areas, sustainable agriculture) |
| **Global Soil & Species Datasets** | ISRIC / GBIF / WorldClim | Global SoilGrids 250m, Global Biodiversity Information Facility, Bioclimatic variables |

---

## 6. Verification and Test Suite

All unit, integration, and end-to-end checks pass cleanly:
- **Scientific Validation Tests**: Ensures missing variables are distinguished from zero, range checks enforce physical boundaries, and compound pressures require ≥3 variables.
- **Frontend Type Safety**: Strict TypeScript compiler checks (`tsc --noEmit`).
- **Production Build**: Clean compilation (`vite build`).

---

## 7. Environment Configuration & Secret Safety

VASUDHA enforces strict secret safety and configuration discipline across all tiers:

1. **Local Setup via `.env.example`**:
   Copy the example environment template to create your local `.env`:
   ```bash
   cp .env.example .env
   ```
2. **Local Configuration**:
   Populate required configuration in `.env` (such as `GEMINI_API_KEY`, `DATABASE_URL`).
3. **No Committed Secrets**:
   `.env`, credentials, local database files (`*.db`), and private keys are ignored by `.gitignore` and must **never** be committed to version control.
4. **No Hardcoded Credentials**:
   Hardcoded API keys, database passwords, and secrets are strictly prohibited anywhere in the codebase, Docker manifests, migration scripts, or documentation.
5. **Architectural Separation (Server vs Client)**:
   - **Server-Side Only**: Sensitive credentials (e.g., `GEMINI_API_KEY`, database passwords, private auth tokens) are exclusively accessed server-side via Pydantic settings. They are never exposed to the frontend browser bundle.
   - **Client-Side Variables**: Only non-sensitive, public configurations prefixed with `VITE_` (e.g. `VITE_API_BASE_URL`) may be exposed to the browser.
6. **Backend Lifecycle**:
   Restart the backend service after making any changes to `.env` or system environment variables.

---

## 8. Quick Start

### Running Locally
```bash
# 1. Install dependencies
npm install

# 2. Run the development server (port 3000)
npm run dev

# 3. Build for production
npm run build
```

---

## 9. Limitations & Scope Discipline

- **Data Resolution**: Global datasets (SoilGrids 250m, WorldClim 1km) provide baseline estimates; on-the-ground soil laboratory assays should verify specific parcel micronutrients.
- **Local Seed Provenance**: Germplasm availability for specific endemic ecotypes must be verified through local community nurseries.
- **Dynamic Hydrology**: 1D soil-moisture balances model local infiltration; regional deep-aquifer groundwater extraction rates require dedicated hydrological telemetry.

---

## 10. Documentation Index

- [System Architecture (docs/architecture.md)](docs/architecture.md)
- [Scientific Grounding & Evidence Hierarchy (docs/scientific-grounding.md)](docs/scientific-grounding.md)
- [Evaluator Demo Guide & Walkthrough (docs/demo.md)](docs/demo.md)
- [Presentation Slide Deck & Demo Script (docs/presentation.md)](docs/presentation.md)
- [Final System Audit Report (docs/final-audit-report.md)](docs/final-audit-report.md)
