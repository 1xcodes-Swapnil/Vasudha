"""Base contracts for the Scientific Evidence & Knowledge layer (Phase 1+)."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class EvidenceStore(ABC):
    """Abstract interface for scientific evidence retrieval.

    Implementation scheduled for future phase.
    """

    @abstractmethod
    def retrieve_evidence(self, query: str, filters: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve peer-reviewed and institutional evidence."""
        pass
