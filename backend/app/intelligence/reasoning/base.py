"""Base contracts for the Ecological Intelligence & Reasoning layer (Phase 1+)."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class EcologicalReasoner(ABC):
    """Abstract interface for multi-metric ecological reasoning.

    Implementation scheduled for future phase.
    """

    @abstractmethod
    def evaluate_pressures(self, environmental_state: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate ecological pressures from observed environmental state variables."""
        pass
