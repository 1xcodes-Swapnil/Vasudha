"""Database repository and synchronization for the Ecological Knowledge Base (Phase 3)."""

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from backend.app.models.knowledge import (
    EcologicalRelationshipModel,
    EnvironmentalMetricModel,
    EvidenceMetadataModel,
)
from backend.app.schemas.knowledge import (
    EcologicalRelationship,
    EnvironmentalMetricDefinition,
    EvidenceMetadata,
)
from backend.app.knowledge.curated_metrics import CURATED_METRICS
from backend.app.knowledge.curated_evidence import CURATED_EVIDENCE
from backend.app.knowledge.curated_relationships import CURATED_RELATIONSHIPS
from backend.app.core.logging import logger


class KnowledgeRepository:
    """Repository handling persistence, seeding, and querying of ecological knowledge."""

    @staticmethod
    def seed_knowledge_base(db: Session) -> Dict[str, int]:
        """Seeds curated metrics, evidence metadata, and ecological relationships into DB if not already present."""
        metrics_added = 0
        evidence_added = 0
        relationships_added = 0

        try:
            # 1. Seed Metrics
            for m in CURATED_METRICS:
                existing_metric = db.query(EnvironmentalMetricModel).filter_by(id=m.id).first()
                if not existing_metric:
                    model = EnvironmentalMetricModel(
                        id=m.id,
                        name=m.name,
                        domain=m.domain.value,
                        unit=m.unit,
                        metric_type=m.metric_type,
                        description=m.description,
                        min_value=m.min_value,
                        max_value=m.max_value,
                        categories_json=m.categories,
                    )
                    db.add(model)
                    metrics_added += 1

            # 2. Seed Evidence
            for e in CURATED_EVIDENCE:
                existing_ev = db.query(EvidenceMetadataModel).filter_by(id=e.id).first()
                if not existing_ev:
                    model = EvidenceMetadataModel(
                        id=e.id,
                        source_type=e.source_type,
                        citation=e.citation,
                        doi=e.doi,
                        year=e.year,
                        institution=e.institution,
                        url=e.url,
                        requires_evidence=e.requires_evidence,
                        confidence_grade=e.confidence_grade,
                    )
                    db.add(model)
                    evidence_added += 1

            # 3. Seed Relationships
            for r in CURATED_RELATIONSHIPS:
                existing_rel = db.query(EcologicalRelationshipModel).filter_by(id=r.id).first()
                if not existing_rel:
                    model = EcologicalRelationshipModel(
                        id=r.id,
                        name=r.name,
                        source_metric=r.source_metric,
                        operator=r.operator.value,
                        threshold_value=r.threshold_value,
                        target_metric=r.target_metric,
                        target_state=r.target_state,
                        relationship_type=r.relationship_type,
                        direction=r.direction.value,
                        ecological_mechanism=r.ecological_mechanism,
                        evidence_ids=r.evidence_ids,
                        evidence_strength=r.evidence_strength.value,
                        confidence=r.confidence,
                        ecosystem_context=r.ecosystem_context,
                        quality_metadata=r.quality_metadata,
                    )
                    db.add(model)
                    relationships_added += 1

            db.commit()
            logger.info(
                f"Knowledge Base seeded: {metrics_added} metrics, "
                f"{evidence_added} evidence sources, {relationships_added} relationships added."
            )
        except Exception as exc:
            db.rollback()
            logger.error(f"Error seeding knowledge base: {exc}")
            raise exc

        return {
            "metrics_seeded": metrics_added,
            "evidence_seeded": evidence_added,
            "relationships_seeded": relationships_added,
        }

    @staticmethod
    def get_all_metrics(
        db: Optional[Session] = None, domain: Optional[str] = None
    ) -> List[EnvironmentalMetricDefinition]:
        """Returns all metrics, optionally filtered by domain."""
        if db is not None:
            try:
                query = db.query(EnvironmentalMetricModel)
                if domain:
                    query = query.filter_by(domain=domain)
                db_models = query.all()
                if db_models:
                    return [
                        EnvironmentalMetricDefinition(
                            id=m.id,
                            name=m.name,
                            domain=m.domain,
                            unit=m.unit,
                            metric_type=m.metric_type,
                            description=m.description,
                            min_value=m.min_value,
                            max_value=m.max_value,
                            categories=m.categories_json,
                        )
                        for m in db_models
                    ]
            except Exception as exc:
                logger.warning(f"Database query failed for metrics ({exc}), falling back to in-memory curated data.")

        # In-memory fallback
        results = CURATED_METRICS
        if domain:
            results = [m for m in results if m.domain.value == domain]
        return results

    @staticmethod
    def get_all_relationships(
        db: Optional[Session] = None,
        source_metric: Optional[str] = None,
        target_metric: Optional[str] = None,
        ecosystem: Optional[str] = None,
    ) -> List[EcologicalRelationship]:
        """Returns ecological relationships with optional filtering."""
        if db is not None:
            try:
                query = db.query(EcologicalRelationshipModel)
                if source_metric:
                    query = query.filter_by(source_metric=source_metric)
                if target_metric:
                    query = query.filter_by(target_metric=target_metric)
                if ecosystem and ecosystem != "all":
                    query = query.filter(
                        (EcologicalRelationshipModel.ecosystem_context == ecosystem)
                        | (EcologicalRelationshipModel.ecosystem_context == "all")
                    )
                db_models = query.all()
                if db_models:
                    return [
                        EcologicalRelationship(
                            id=r.id,
                            name=r.name,
                            source_metric=r.source_metric,
                            operator=r.operator,
                            threshold_value=r.threshold_value,
                            target_metric=r.target_metric,
                            target_state=r.target_state,
                            relationship_type=r.relationship_type,
                            direction=r.direction,
                            ecological_mechanism=r.ecological_mechanism,
                            evidence_ids=r.evidence_ids or [],
                            evidence_strength=r.evidence_strength,
                            confidence=r.confidence,
                            ecosystem_context=r.ecosystem_context,
                            quality_metadata=r.quality_metadata or {},
                        )
                        for r in db_models
                    ]
            except Exception as exc:
                logger.warning(f"Database query failed for relationships ({exc}), falling back to in-memory curated data.")

        # In-memory fallback
        results = CURATED_RELATIONSHIPS
        if source_metric:
            results = [r for r in results if r.source_metric == source_metric]
        if target_metric:
            results = [r for r in results if r.target_metric == target_metric]
        if ecosystem and ecosystem != "all":
            results = [r for r in results if r.ecosystem_context in (ecosystem, "all")]
        return results

    @staticmethod
    def get_all_evidence(
        db: Optional[Session] = None, institution: Optional[str] = None
    ) -> List[EvidenceMetadata]:
        """Returns evidence sources, optionally filtered by publishing institution."""
        if db is not None:
            try:
                query = db.query(EvidenceMetadataModel)
                if institution:
                    query = query.filter_by(institution=institution)
                db_models = query.all()
                if db_models:
                    return [
                        EvidenceMetadata(
                            id=e.id,
                            source_type=e.source_type,
                            citation=e.citation,
                            doi=e.doi,
                            year=e.year,
                            institution=e.institution,
                            url=e.url,
                            requires_evidence=e.requires_evidence,
                            confidence_grade=e.confidence_grade,
                        )
                        for e in db_models
                    ]
            except Exception as exc:
                logger.warning(f"Database query failed for evidence ({exc}), falling back to in-memory curated data.")

        # In-memory fallback
        results = CURATED_EVIDENCE
        if institution:
            results = [e for e in results if e.institution == institution]
        return results
