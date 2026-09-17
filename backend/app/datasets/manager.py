"""Environmental Dataset Manager & Orchestration Engine (Phase 7).

Coordinates multi-domain authoritative environmental dataset adapters,
executes comprehensive point queries, handles state enrichment,
and maintains dataset registries and provenance records.
"""

from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session

from backend.app.schemas.dataset import (
    DatasetMetadata,
    RawDatasetObservation,
    DataQualityCheck,
    DataQualityReport,
    VariableProvenance,
    PointQueryResult,
    StateEnrichmentRequest,
    StateEnrichmentResponse,
    DataQualitySeverity,
    QualityFlagType,
)
from backend.app.schemas.environmental_state import (
    EnvironmentalState,
    SoilState,
    LandState,
    BiodiversityState,
    ClimateState,
    HumanImpactState,
    SpatialContext,
)
from backend.app.datasets.metadata import AUTHORITATIVE_DATASETS
from backend.app.datasets.base_adapter import DatasetAdapter
from backend.app.datasets.adapters import (
    SoilGridsAdapter,
    CopernicusLandCoverAdapter,
    GBIFBiodiversityAdapter,
    WorldClimClimateAdapter,
    GlobalForestWatchAdapter,
    UNEPPollutionAdapter,
)
from backend.app.datasets.pipeline import EnvironmentalDataPipeline
from backend.app.services.geo.manager import resolve_geo_context
from backend.app.models.dataset import DatasetRegistryModel, IngestedObservationModel
from backend.app.core.logging import logger


class EnvironmentalDatasetManager:
    """Central registry and query orchestrator for authoritative environmental data sources."""

    def __init__(self):
        self._adapters: Dict[str, DatasetAdapter] = {
            "soilgrids_isric": SoilGridsAdapter(),
            "copernicus_worldcover": CopernicusLandCoverAdapter(),
            "gbif_occurrence": GBIFBiodiversityAdapter(),
            "worldclim_v2": WorldClimClimateAdapter(),
            "global_forest_watch": GlobalForestWatchAdapter(),
            "unep_sedac_pollution": UNEPPollutionAdapter(),
        }

    def list_datasets(self) -> List[DatasetMetadata]:
        """Return metadata list for all registered authoritative datasets."""
        return list(AUTHORITATIVE_DATASETS.values())

    def get_dataset(self, dataset_id: str) -> Optional[DatasetMetadata]:
        """Retrieve metadata for a specific dataset."""
        return AUTHORITATIVE_DATASETS.get(dataset_id)

    def get_adapter(self, dataset_id: str) -> Optional[DatasetAdapter]:
        """Retrieve adapter instance for a dataset."""
        return self._adapters.get(dataset_id)

    def seed_registry_db(self, db_session: Session) -> int:
        """Seed dataset registry table in the database if empty or out of date."""
        seeded_count = 0
        try:
            for ds_id, meta in AUTHORITATIVE_DATASETS.items():
                existing = db_session.query(DatasetRegistryModel).filter_by(id=ds_id).first()
                if not existing:
                    reg_model = DatasetRegistryModel(
                        id=meta.id,
                        name=meta.name,
                        source_organization=meta.source_organization,
                        source_url=meta.source_url,
                        license=meta.license,
                        domain=meta.domain,
                        variables_json=meta.variables,
                        raw_units_json=meta.raw_units,
                        canonical_units_json=meta.canonical_units,
                        geographic_coverage=meta.geographic_coverage,
                        temporal_coverage=meta.temporal_coverage,
                        spatial_resolution=meta.spatial_resolution,
                        retrieval_date=meta.retrieval_date,
                        provenance=meta.provenance,
                        known_limitations_json=meta.known_limitations,
                        is_authoritative=meta.is_authoritative,
                    )
                    db_session.add(reg_model)
                    seeded_count += 1
            if seeded_count > 0:
                db_session.commit()
                logger.info(f"Seeded {seeded_count} authoritative datasets into DatasetRegistryModel.")
        except Exception as exc:
            db_session.rollback()
            logger.warning(f"Error seeding dataset registry: {exc}")
        return seeded_count

    def query_point(
        self,
        latitude: float,
        longitude: float,
        allow_synthetic: bool = False,
        db_session: Optional[Session] = None,
    ) -> PointQueryResult:
        """Query all authoritative datasets for a given geographic point.

        Coordinates are validated. Geographic region & ecosystem context are resolved.
        Returns merged EnvironmentalState with comprehensive provenance and quality audit.
        """
        # 1. Geographic context lookup
        geo_context = resolve_geo_context(latitude, longitude, allow_degraded=True)
        region = geo_context.region
        ecosystem = geo_context.ecosystem

        merged_state_dict: Dict[str, Any] = {
            "soil": {},
            "land": {},
            "biodiversity": {},
            "climate": {},
            "human_impact": {},
            "spatial_context": {
                "latitude": round(latitude, 6),
                "longitude": round(longitude, 6),
                "region": region,
                "ecosystem": ecosystem,
            },
        }

        all_provenance: Dict[str, VariableProvenance] = {}
        all_checks: List[DataQualityCheck] = []
        missing_vars: List[str] = []
        zero_vars: List[str] = []
        datasets_queried: List[str] = []
        has_synthetic = False

        # Add spatial coordinate checks
        coord_checks = EnvironmentalDataPipeline.validate_coordinates(latitude, longitude)
        all_checks.extend(coord_checks)

        # 2. Iterate each authoritative adapter
        for ds_id, adapter in self._adapters.items():
            datasets_queried.append(ds_id)
            try:
                raw_obs = adapter.fetch_point(
                    latitude=latitude,
                    longitude=longitude,
                    is_synthetic_allowed=allow_synthetic,
                )

                if raw_obs.is_synthetic:
                    has_synthetic = True

                canonical_vals, q_checks, prov_map = adapter.normalize_and_validate(raw_obs)
                all_checks.extend(q_checks)
                all_provenance.update(prov_map)

                # Merge values into domain dictionary
                for var_path, val in canonical_vals.items():
                    domain, metric = var_path.split(".", 1)
                    if domain in merged_state_dict:
                        merged_state_dict[domain][metric] = val
                        if val == 0 or val == 0.0:
                            zero_vars.append(var_path)

            except Exception as exc:
                logger.error(f"Error querying dataset adapter '{ds_id}': {exc}")
                all_checks.append(
                    DataQualityCheck(
                        metric_name=f"{adapter.metadata.domain}.*",
                        flag_type=QualityFlagType.ADAPTER_DEGRADED,
                        severity=DataQualitySeverity.WARNING,
                        message=f"Adapter '{ds_id}' failed during point query: {exc}",
                    )
                )

        # 3. Check for any missing variables across all domains
        for ds_id, meta in AUTHORITATIVE_DATASETS.items():
            for var in meta.variables:
                domain, metric = var.split(".", 1)
                val = merged_state_dict.get(domain, {}).get(metric)
                if val is None:
                    missing_vars.append(var)

        # 4. Construct canonical state
        canonical_state = EnvironmentalState.model_validate(merged_state_dict)

        # 5. Build DataQualityReport
        errors_count = sum(1 for c in all_checks if c.severity == DataQualitySeverity.ERROR)
        warnings_count = sum(1 for c in all_checks if c.severity == DataQualitySeverity.WARNING)
        passed_count = sum(1 for c in all_checks if c.severity == DataQualitySeverity.INFO)
        is_valid = errors_count == 0

        quality_report = DataQualityReport(
            total_checks=len(all_checks),
            passed_checks=passed_count,
            warnings_count=warnings_count,
            errors_count=errors_count,
            is_valid=is_valid,
            checks=all_checks,
            missing_variables=missing_vars,
            zero_variables=zero_vars,
            synthetic_count=1 if has_synthetic else 0,
        )

        # 6. Persist merged point observation if db_session is provided
        if db_session is not None:
            try:
                obs_model = IngestedObservationModel(
                    dataset_id="multi_authoritative_harmonized",
                    latitude=latitude,
                    longitude=longitude,
                    region=region,
                    ecosystem=ecosystem,
                    raw_payload_json={"datasets": datasets_queried},
                    normalized_state_json=canonical_state.model_dump(),
                    provenance_json={k: v.model_dump() for k, v in all_provenance.items()},
                    quality_report_json=quality_report.model_dump(),
                    is_valid=is_valid,
                    is_synthetic=has_synthetic,
                )
                db_session.add(obs_model)
                db_session.commit()
            except Exception as exc:
                db_session.rollback()
                logger.warning(f"Failed to persist multi-dataset point observation: {exc}")

        return PointQueryResult(
            latitude=round(latitude, 6),
            longitude=round(longitude, 6),
            canonical_state=canonical_state,
            provenance_records=all_provenance,
            quality_report=quality_report,
            datasets_queried=datasets_queried,
            is_fully_authoritative=not has_synthetic,
            has_synthetic_data=has_synthetic,
        )

    def enrich_state(
        self,
        request: StateEnrichmentRequest,
        db_session: Optional[Session] = None,
    ) -> StateEnrichmentResponse:
        """Enrich an existing EnvironmentalState using authoritative datasets.

        Preserves user-defined variables unless overwrite_existing=True.
        Fills in missing null metrics.
        """
        lat = request.latitude if request.latitude is not None else request.state.spatial_context.latitude
        lon = request.longitude if request.longitude is not None else request.state.spatial_context.longitude

        if lat is None or lon is None:
            raise ValueError("Coordinates (latitude and longitude) must be present on state or payload to perform enrichment.")

        point_result = self.query_point(
            latitude=lat,
            longitude=lon,
            allow_synthetic=request.allow_synthetic_fallback,
            db_session=db_session,
        )

        dataset_state = point_result.canonical_state
        base_state = request.state

        metrics_added = 0
        metrics_preserved = 0

        final_dict = base_state.model_dump()
        ds_dict = dataset_state.model_dump()

        # Merge domains
        for domain in ["soil", "land", "biodiversity", "climate", "human_impact", "spatial_context"]:
            base_dom = final_dict.get(domain, {})
            ds_dom = ds_dict.get(domain, {})

            for key, ds_val in ds_dom.items():
                base_val = base_dom.get(key)
                if base_val is not None and not request.overwrite_existing:
                    metrics_preserved += 1
                elif ds_val is not None:
                    base_dom[key] = ds_val
                    metrics_added += 1

            final_dict[domain] = base_dom

        enriched_state = EnvironmentalState.model_validate(final_dict)

        return StateEnrichmentResponse(
            enriched_state=enriched_state,
            metrics_added_count=metrics_added,
            metrics_preserved_count=metrics_preserved,
            provenance_records=point_result.provenance_records,
            quality_report=point_result.quality_report,
        )


# Global singleton instance
dataset_manager = EnvironmentalDatasetManager()
