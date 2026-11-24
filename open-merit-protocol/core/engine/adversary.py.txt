import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List

@dataclass
class SimulationSession:
    session_id: str
    builder_pubkey: str
    cartridge_id: str
    current_elo: float
    events: List[Dict[str, Any]] = field(default_factory=list)

    def log_step(self, step_type: str, payload: Dict[str, Any]) -> None:
        self.events.append({
            "ts": time.time(),
            "type": step_type,  # 'STATE_INIT', 'BUILDER_ACTION', 'ADVERSARIAL_PERTURBATION', 'OUTCOME'
            "payload": payload
        })

    def compute_elo_update(self, task_difficulty_elo: float, objective_score: float, k_factor: float = 32.0) -> float:
        """Updates builder Elo based on deterministic ground-truth outcome (0.0 to 1.0)."""
        expected = 1.0 / (1.0 + 10 ** ((task_difficulty_elo - self.current_elo) / 400.0))
        self.current_elo = round(self.current_elo + k_factor * (objective_score - expected), 2)
        return self.current_elo

    def finalize_proof_hash(self) -> str:
        canonical = json.dumps(self.events, sort_keys=True).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()