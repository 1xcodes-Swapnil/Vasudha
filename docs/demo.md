# Evaluator Demo Guide & Walkthrough

> **VASUDHA — Biodiversity Intelligence for a Living Earth**

This guide provides a reproducible, step-by-step walkthrough for evaluating VASUDHA's end-to-end ecological intelligence pipeline.

---

## 1. Demo Scenario Overview

### Scenario: Degraded Semi-Arid Monoculture Cropland
- **Ecosystem**: Tropical Dry Deciduous / Cropland Ecotone
- **Geographic Coordinates**: 12.9716° N, 77.5946° E (Deccan Plateau, India)
- **Ecoregion**: Semi-arid rain-shadow plateau characterized by intense monsoonal dry-spells and high seasonal evaporation rates.

### Scientific Rationale for Baseline Values:
| Variable | Value | Ecological Interpretation |
| :--- | :--- | :--- |
| **Soil Organic Carbon (SOC)** | **0.8%** (8.0 g/kg) | Severely depleted below FAO critical threshold of 1.0%; indicates loss of soil microbial biomass and collapsed macro-aggregation. |
| **Soil Moisture** | **14.0%** | Critical dry-season deficit; plants approaching permanent wilting point. |
| **Soil pH** | **5.4** | Moderately acidic; limits phosphorus bioavailability and nodulation in unadapted legumes. |
| **Annual Rainfall** | **480.0 mm/yr** | Sub-humid semi-arid regime with high variability. |
| **Mean Temperature** | **32.5 °C** | High evaporative demand and thermal surface stress. |
| **Habitat Diversity Score** | **22.0 / 100** | Monoculture simplification; absence of non-crop woody perennials or hedge corridors. |
| **Species Richness** | **18 species** | Impoverished floral and avian biodiversity compared to regional reference baseline (~65+). |
| **Deforestation / Canopy Loss** | **14.5%** | Removal of boundary tree corridors and shade canopy. |

---

## 2. Step-by-Step Evaluator Walkthrough

### Step 1: Initialize Baseline in Environment View
1. Navigate to the **Environment** tab in the main navigation.
2. In the **Evaluator Benchmark Scenarios** card, verify that **"Degraded Semi-Arid Cropland (Primary Benchmark)"** is active (marked with a green badge).
3. Click **"Validate State"** in the top control bar.
   - *Verification*: A confirmation banner appears verifying that all biophysical variables comply with valid physical ranges.
4. Toggle **"Authoritative Datasets"** to inspect data provenance (ISRIC SoilGrids 250m, WorldClim, GBIF).

### Step 2: Inspect Geographic Context in Map View
1. Navigate to the **Map** tab.
2. View the parcel marker located at **12.9716° N, 77.5946° E**.
3. Observe the regional biome context (*Tropical Dry Deciduous Forest / Agro-ecosystem Ecotone*) and elevation/precipitation baselines.

### Step 3: Inspect Multi-Metric Reasoning & Causal Flow
1. Navigate to the **Reasoning** tab.
2. In the **Causal Flow** sub-tab, observe the 7-stage chain computed directly from the canonical state:
   - **Step 1 (Observed)**: Depleted SOC (0.8%), acute moisture deficit (14%), low structural diversity (22/100).
   - **Step 2 (Ecological Pressures)**: Water Deficit Stress + Soil Degradation Strain + Habitat Fragmentation.
   - **Step 3 (Mechanisms)**: Hydrological-biophysical uncoupling; stomatal conductance restriction and aggregate loss.
   - **Step 4 (Implications)**: Contraction of avian nesting strata and soil macroinvertebrate refugia.
   - **Step 5 (Interventions)**: Multistrata Agroforestry, Cover Cropping, Riparian Buffers.
   - **Step 6 (Directional Metric Direction)**: ↑ SOC, ↑ Infiltration, ↑ Structural Diversity, ↓ Thermal Peak Stress.
   - **Step 7 (Scientific Evidence)**: IPCC AR6 WGII Chapter 2, IPBES Global Assessment, FAO GSOCseq.
3. Switch to the **Multi-Metric Matrix** sub-tab to inspect the 2-variable and 3-variable compound triggers.
4. Switch to the **Nature Risk Profile** sub-tab to view risk scores for Water Stress (Critical), Habitat Pressure (High), and Climate Exposure (High).

### Step 4: Query via Conversational Intelligence
1. Navigate to the **Intelligence** tab.
2. Review the pre-loaded contextual message or submit a test prompt:
   - *Query*: `"What ecological interventions are recommended for this degraded semi-arid cropland with 0.8% soil carbon?"`
3. Observe the structured, evidence-grounded response:
   - Contains explicit biophysical reasoning across rainfall, soil carbon, and moisture.
   - Cites Tier-1 scientific literature (IPCC AR6 WGII, FAO).
   - Distinguishes directional estimates from definitive measurements.

### Step 5: Review Audited Interventions & Action Plans
1. Navigate to the **Actions** tab.
2. Review the audited recommendation cards:
   - **Multistrata Agroforestry with Native Leguminous Perennials** (Feasibility: Suitable | High Confidence)
   - **Cover Cropping & Surface Residue Mulching** (Feasibility: Suitable | High Confidence)
   - **Perennial Contour Vegetative Buffers** (Feasibility: Suitable | High Confidence)
3. For each recommendation, observe the required criteria:
   - **What to do**: Clear operational prescription.
   - **Why it works**: Biophysical explanation.
   - **Impacted Metrics**: Directional indicators (↑ Soil Organic Carbon, ↑ Infiltration).
   - **Time Horizon**: Realistic implementation schedule (e.g. 3–5 years).
   - **Context-Specific Trade-offs**: E.g., initial juvenile shade regulation and water allocation during establishment.

### Step 6: Trigger Progressive Disclosure ("Why this intervention?")
1. On any recommendation card in the **Actions** tab, click **"Why this intervention? (Full Auditable Explanation Chain)"**.
2. An auditable matrix expands, showing:
   1. *Observed Conditions Summary*
   2. *Addressed Ecological Pressure*
   3. *Biophysical Mechanism*
   4. *Scientific Validation & Confidence Basis*
   5. *Retrieved Evidence Passages* (with exact citations to IPCC, IPBES, and FAO)
   6. *Implementation Constraints & Scientific Limitations*

---

## 3. How to Reset the Demo

To return the entire system to the default benchmark state:
1. Navigate to the **Environment** tab.
2. Click **"Load"** under the **"Degraded Semi-Arid Cropland"** card.
3. All views (Reasoning, Actions, Map, Intelligence) immediately re-synchronize to the canonical state.
