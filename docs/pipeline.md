# Ecological Reasoning & Hybrid Layered RAG Pipeline

This document defines the scientific intelligence pipeline for the **Darukaa.Earth Biodiversity Intelligence Platform**.

## Core Principle: Grounded Scientific Intelligence

> **The Large Language Model is NOT the scientific source of truth.**
> Scientific validity is established through structured multi-metric reasoning, deterministic domain rules, and vector-grounded scientific literature (IPCC, IPBES, FAO, UNEP, CBD).

---

## 13-Stage Pipeline Sequence

```
[1. User Input]
       │
       ▼
[2. Environmental State Normalization] (Soil, Land, Biodiversity, Climate, Human Impact)
       │
       ▼
[3. Geo Context Resolution] (Coordinates, Ecoregion, Biome Baselines)
       │
       ▼
[4. Multi-Metric Reasoning] (Cross-variable ecological pressure evaluation across ≥3 metrics)
       │
       ▼
[5. Scientific RAG Retrieval] (Hybrid vector + structured queries from IPCC/IPBES/FAO)
       │
       ▼
[6. Nature Risk Profile] (Degradation vectors, tipping point analysis, biodiversity loss risk)
       │
       ▼
[7. Ecological Intervention Engine] (Biome-compatible restoration & mitigation actions)
       │
       ▼
[8. Feasibility & Constraint Check] (Climatic, seasonal, soil suitability, resource constraints)
       │
       ▼
[9. Evidence Mapping] (Direct citation attribution with confidence intervals)
       │
       ▼
[10. Scientific Claim Validation] (Guardrail verifying quantitative claims against evidence)
       │
       ▼
[11. Explainability Generation] (Condition → Pressure → Mechanism → Intervention → Metric effects)
       │
       ▼
[12. Context-Specific Trade-off Analysis] (Ecological, land-use, resource, and temporal trade-offs)
       │
       ▼
[13. Structured Response Synthesis] (Actionable report with confidence and limitations)
```

---

## Environmental State Metric Domains

The platform tracks and evaluates across 6 primary ecological dimensions:

1. **Soil Properties**:
   - pH (acidity / alkalinity)
   - Soil Organic Carbon (SOC %)
   - Moisture & water holding capacity
   - Bulk density & erosion risk

2. **Land & Cover**:
   - Land cover category (forest, grassland, wetland, cropland, degraded)
   - Canopy cover (%)
   - Land use history and degradation stage

3. **Biodiversity Indicators**:
   - Species richness index
   - Habitat diversity & connectivity
   - Native vs. invasive species dominance
   - Keystone species presence

4. **Climate Regimes**:
   - Mean annual precipitation (mm/year) & seasonal distribution
   - Temperature ranges & extreme weather frequency
   - Aridity index & evapotranspiration

5. **Human Pressures**:
   - Deforestation / fragmentation rate
   - Agricultural run-off, nitrogen/phosphorus loading, chemical pollution
   - Grazing intensity & human encroachment

6. **Geographic & Biome Context**:
   - Coordinates (latitude, longitude)
   - Biome / ecoregion classification (e.g. Tropical Moist Forest, Montane Grassland)
   - Elevation and slope

---

## Mandatory Reasoning Rules

1. **Multi-Metric Triangulation**:
   Recommendations must synthesize across at least **3 environmental variables** (e.g., Soil pH + Precipitation + Land Cover) before recommending interventions.

2. **Explainability Requirement ("Why This Intervention?")**:
   Every recommendation must explicitly present the causal chain:
   $$\text{Observed Conditions} \longrightarrow \text{Ecological Pressure} \longrightarrow \text{Biological Mechanism} \longrightarrow \text{Intervention} \longrightarrow \text{Expected Metric Effects} \longrightarrow \text{Peer-Reviewed Evidence}$$

3. **Mandatory Output Schema**:
   Each proposed intervention must provide:
   - **What to do**: Precise restorative or protective action.
   - **Why it works**: Direct ecological mechanism.
   - **Ecological reasoning**: Cross-metric justification.
   - **Impacted metrics**: Expected directional shifts in environmental state variables.
   - **Time horizon**: Short-term (1–2 yrs), medium-term (3–5 yrs), or long-term (10+ yrs).
   - **Evidence & Citations**: Direct reference to IPCC, IPBES, FAO, or peer-reviewed literature.
   - **Confidence Level**: High, Medium, or Low with quantitative bounds.
   - **Constraints & Feasibility**: Climatic, soil, and operational preconditions.
   - **Context-Specific Trade-offs**: Ecological and socio-economic trade-offs.
   - **Limitations & Unknowns**: Explicit identification of missing data.
