# Geographic Context & Interactive Map Specification (Phase 2)

## 1. Overview & Objective

Phase 2 establishes spatial grounding for the Darukaa.Earth Biodiversity Intelligence system. It integrates coordinates, region name, and ecosystem classification with the canonical `EnvironmentalState` while ensuring the core intelligence and reasoning pipelines remain fully operational even if geospatial services or visual map tiles are unavailable.

## 2. Spatial Data Model Integration

The `SpatialContext` model forms the 6th canonical category of `EnvironmentalState`:

```
EnvironmentalState
├── soil (ph, organic_carbon, moisture)
├── land (land_use, land_cover)
├── biodiversity (species_richness, habitat_diversity)
├── climate (temperature, rainfall)
├── human_impact (pollution, deforestation)
└── spatial_context
    ├── latitude (float [-90.0, 90.0])
    ├── longitude (float [-180.0, 180.0])
    ├── region (string [max 128 chars], e.g., 'Western Ghats')
    └── ecosystem (string [max 128 chars], e.g., 'Tropical Moist Broadleaf Forest')
```

### Non-Destructive Update Semantics
Updating or clearing coordinates modifies exclusively `state.spatial_context`. All metrics under `soil`, `land`, `biodiversity`, `climate`, and `human_impact` remain strictly untouched.

---

## 3. GeoContextProvider Abstraction Architecture

To avoid vendor lock-in or fragile couplings to third-party commercial mapping APIs, Phase 2 implements a decoupled provider interface:

```python
class GeoContextProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def description(self) -> str: ...

    @abstractmethod
    def lookup(self, latitude: float, longitude: float) -> GeoContextResult: ...

    def health_check(self) -> Dict[str, Any]: ...

    def enrich_external_datasets(self, latitude: float, longitude: float) -> Dict[str, Any]: ...
```

### Implemented Providers
1. **`RuleBasedGeoContextProvider` (`rule_based_local`)**:
   - Deterministic local spatial resolution based on WWF Terrestrial Biomes and ecological bounding boxes (Western Ghats, Amazon Basin, Deccan Plateau, Fennoscandia, Serengeti, Sundarbans, Cerrado, Congo Basin, Mediterranean, etc.).
   - Includes latitudinal biome fallbacks for unmapped coordinates.
   - Zero external network dependencies (100% offline resilience).

2. **`FailingGeoContextProvider` (`mock_failing_provider`)**:
   - Simulates external service downtime and upstream network timeouts for resilience validation.

---

## 4. Graceful Degradation Behavior

| Failure Mode | System Behavior |
| :--- | :--- |
| **Invalid Coordinates** (e.g., Lat > 90° or Lon > 180°) | Rejected with HTTP 422 Unprocessable Entity; descriptive error message displayed. |
| **Geospatial Service Offline / Upstream Outage** | Coordinates are preserved; `region` and `ecosystem` are marked as `null` (Unknown); `degraded=true` flag returned. No crashes. |
| **Missing Coordinates** | Fields remain `null`; spatial context defaults to unpinned state. |
| **Map Tile Server / Canvas Failure** | `GeoContextMap` activates fallback rendering mode; numeric coordinate inputs and benchmark buttons remain fully functional. |

---

## 5. API Endpoints

- `POST /api/v1/geo/lookup`: Resolves region, ecosystem, biome code, and confidence from latitude/longitude.
- `POST /api/v1/geo/sync-state`: Synchronizes coordinates into an `EnvironmentalState`, auto-enriching ecosystem or clearing location.
- `GET /api/v1/geo/providers`: Lists registered providers and operational statuses.
- `POST /api/v1/geo/providers/switch`: Switches the active provider for testing or production deployment.

---

## 6. Future Extension Points

1. **Copernicus / Sentinel-2 Land Cover**:
   - Implement `CopernicusGeoContextProvider` deriving real-time 10m land cover rasters.
2. **NASA FIRMS & Global Forest Watch**:
   - Enrich `enrich_external_datasets()` with canopy height and deforestation baseline metrics.
3. **SoilGrids / ISRIC**:
   - Auto-suggest baseline soil pH and organic carbon priors for unmeasured coordinates.
