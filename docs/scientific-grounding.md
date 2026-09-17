# Scientific Grounding & Evidence Hierarchy

> **VASUDHA — Biodiversity Intelligence for a Living Earth**

VASUDHA is designed from first principles with a fundamental scientific constraint: **the Large Language Model is never the scientific source of truth**. Natural language generation is strictly bounded by structured biophysical rules, empirical dataset ingestion, and peer-reviewed consensus evidence retrieved from global scientific bodies.

---

## 1. Evidence Hierarchy

Every claim, biophysical mechanism, and intervention recommendation in VASUDHA is validated against a formal three-tier evidence hierarchy:

```
┌────────────────────────────────────────────────────────────────────────┐
│  TIER 1: GLOBAL INTERGOVERNMENTAL CONSENSUS (Highest Authority)         │
│  • IPCC Assessment Reports (AR6 WGII: Terrestrial & Freshwater)        │
│  • IPBES Global Assessment on Biodiversity and Ecosystem Services      │
│  • FAO Global Soil Partnership (GSOCseq, State of the World's Land)    │
│  • UNEP Nature-Based Solutions Guidelines                              │
│  • CBD Kunming-Montreal Global Biodiversity Framework Targets          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│  TIER 2: PEER-REVIEWED SYNTHESES & META-ANALYSES                       │
│  • Systematic reviews with quantitative effect sizes                   │
│  • Global meta-analyses published in peer-reviewed journals            │
│    (e.g., Nature, Science, Global Change Biology, Agroforestry Systems) │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│  TIER 3: REGIONAL EMPIRICAL RESTORATION TRIALS                         │
│  • Field validation trials published by national agroforestry institutes│
│    (e.g., ICRAF, CGIAR, EMBRAPA, ICAR)                                 │
└────────────────────────────────────────────────────────────────────────┘
```

### Strictly Excluded Sources
- Unverified blog posts, marketing materials, and promotional vendor whitepapers.
- Ungrounded LLM-synthesized statistics or extrapolated percentage gains without citation.
- Single-trial unreviewed case studies with non-reproducible methodologies.

---

## 2. Authoritative Datasets & Biophysical Parameters

VASUDHA ingests and standardizes data across six core environmental domains:

| Domain | Canonical Variable | Authoritative Source | Unit | Typical Range | Physical Boundary Checks |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Soil** | Soil Organic Carbon (SOC) | ISRIC SoilGrids 250m / FAO GSOC | % (or g/kg) | 0.2% – 8.0% | `0.0 <= soc <= 100.0` |
| **Soil** | Soil pH | ISRIC SoilGrids 250m | pH scale | 3.5 – 9.5 | `0.0 <= ph <= 14.0` |
| **Soil** | Soil Moisture Content | SMAP / Copernicus / In-situ | % volume | 5.0% – 60.0% | `0.0 <= moisture <= 100.0` |
| **Climate** | Annual Precipitation | WorldClim 2.1 (BIO12) / CHIRPS | mm / year | 100 – 4000 mm | `0.0 <= rainfall <= 12000` |
| **Climate** | Mean Annual Temperature | WorldClim 2.1 (BIO1) / ERA5 | °C | -10.0°C – 45.0°C | `-50.0 <= temp <= 60.0` |
| **Biodiversity** | Species Richness | GBIF (Global Biodiversity Facility) | integer count | 5 – 250+ | `richness >= 0` |
| **Biodiversity** | Habitat Diversity Index | Shannon-Wiener structural score | index 0–100 | 10 – 95 | `0.0 <= diversity <= 100.0` |
| **Land Cover** | Land Cover Class | Copernicus Global Land 100m | categorical | UN-LCCS classes | Categorical ontology check |
| **Human Impact** | Canopy Deforestation Loss | Global Forest Watch (Hansen et al.)| % loss / decade | 0.0% – 80.0% | `0.0 <= loss <= 100.0` |
| **Human Impact** | Chemical Pollution Index | UNEP Global Environmental Monitor | index 0–100 | 0 – 100 | `0.0 <= pollution <= 100.0` |

---

## 3. Multi-Metric Ecological Reasoning

Single-variable analyses lead to catastrophic restoration failures (e.g. planting trees in areas with adequate temperature but negative soil water balances). VASUDHA requires simultaneous reasoning across **at least three biophysical variables**:

### Compound Pressure 1: Water Deficit & Soil Aggregate Breakdown
- **Triggering Condition**:
  $$\text{Precipitation} < 600\,\text{mm/yr} \quad \land \quad \text{Soil Moisture} < 18\% \quad \land \quad \text{Soil Organic Carbon} < 1.2\%$$
- **Ecological Mechanism**:
  Depleted organic carbon reduces microbial polysaccharide exudation, causing soil macro-aggregate breakdown. During dry periods, topsoil forms an impenetrable crust, preventing rainfall infiltration. Subsequent convective storms cause severe sheet erosion rather than recharging the rhizosphere.
- **Directional Counter-Intervention**:
  Surface organic mulch combined with deep-rooting leguminous perennials to restore organic matter, reduce surface evaporation by 30–40%, and re-establish root macropore channels.

### Compound Pressure 2: Niche Simplification & Trophic Vulnerability
- **Triggering Condition**:
  $$\text{Habitat Diversity} < 35/100 \quad \land \quad \text{Land Use} = \text{Monoculture} \quad \land \quad \text{Canopy Loss} > 10\%$$
- **Ecological Mechanism**:
  Uniform vertical vegetation structure eliminates microclimatic refugia and structural nesting niches. Absence of sequential floral bloom throughout the dry season causes native pollinator populations to collapse, preventing native seed set.
- **Directional Counter-Intervention**:
  Establishment of 20–30m multi-strata native flowering vegetative corridors along parcel margins and riparian contours to restore pollinator foraging continuity.

---

## 4. Anti-Hallucination & Claim Validation Protocol

Every statement produced by VASUDHA passes through an automated claim validation filter:

1. **Numeric Claim Audit**:
   - Fabricated quantitative assertions (e.g. "increases yields by 73.4% in 90 days") are strictly blocked.
   - All quantitative references must cite empirical benchmark ranges from retrieved consensus documents or be explicitly framed as directional trajectories (e.g., "Expected trajectory: Positive soil carbon accumulation over 3–5 year horizon").
2. **Distinction of Unknown vs. Zero**:
   - A metric with missing data is assigned a status of `UNKNOWN (null)` with an associated uncertainty penalty.
   - It is never coerced to `0`, preventing erroneous triggers (e.g. assuming 0°C temperature or 0mm rainfall when data has merely not been collected).
3. **Biophysical Guardrail Enforcement**:
   - If an intervention is requested for an inappropriate biome (e.g., wetland restoration in an arid steppe), the feasibility engine marks the action `Not Suitable` and presents the biophysical limitation.
4. **Mandatory Trade-off Identification**:
   - Every recommendation must present real-world ecological, logistical, or land-use trade-offs (e.g., initial water competition during establishment phase, labor requirements for hedgerow pruning).

---

## 5. Bibliography of Core Scientific References

- **IPCC (2022)**: *Climate Change 2022: Impacts, Adaptation and Vulnerability.* Contribution of Working Group II to the Sixth Assessment Report of the Intergovernmental Panel on Climate Change. Cambridge University Press.
- **IPBES (2019)**: *Global Assessment Report on Biodiversity and Ecosystem Services of the Intergovernmental Science-Policy Platform on Biodiversity and Ecosystem Services.* Díaz, S., Settele, J., Brondízio, E.S., et al. (eds). IPBES Secretariat, Bonn, Germany.
- **FAO (2022)**: *Recarbonizing Global Soils: A technical manual of recommended management practices.* Food and Agriculture Organization of the United Nations, Rome.
- **FAO & ITPS (2020)**: *State of Knowledge of Soil Biodiversity: Status, challenges and potentialities.* FAO, Rome.
- **UNEP (2021)**: *Making Peace with Nature: A scientific blueprint to tackle the climate, biodiversity and pollution emergencies.* United Nations Environment Programme, Nairobi.
- **CBD (2022)**: *Kunming-Montreal Global Biodiversity Framework.* Conference of the Parties to the Convention on Biological Diversity, Fifteenth Meeting, Montreal.
- **Pörtner, H.-O., et al. (2021)**: *IPBES-IPCC Co-Sponsored Workshop Report on Biodiversity and Climate Change.* IPBES and IPCC.
- **ISRIC (2020)**: *SoilGrids250m: Global gridded soil information based on machine learning.* ISRIC — World Soil Information.
- **WorldClim (2020)**: *WorldClim 2.1: Global climate data for 1970–2000.* Fick, S.E. & Hijmans, R.J. International Journal of Climatology.
