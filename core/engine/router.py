import math
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class VerifiedCandidate:
    candidate_id: str
    public_key_hex: str
    skill_vector: Dict[str, float]          # e.g., {"robotics_controls": 0.91, "perturbation_recovery": 0.88}
    verified_elos: Dict[str, int]           # e.g., {"robotics.control.v1": 1840}
    signature_valid: bool = True
    outcome_multiplier: float = 1.0         # Adjusted dynamically by real-world trial feedback


@dataclass
class EmployerQuery:
    query_id: str
    required_cartridge: str
    min_elo: int
    domain_weights: Dict[str, float]        # Constraint weights; strictly zero degree/pedigree fields
    max_results: int = 10


@dataclass
class MatchResult:
    candidate_id: str
    match_score: float
    verified_elo: int
    domain_alignment: float
    rationale: Dict[str, Any] = field(default_factory=dict)


class MeritRouter:
    """
    Two-sided zero-credential router and outcome feedback engine.
    Matches cryptographically attested capability vectors against constraint queries.
    """

    def __init__(self, k_factor: float = 24.0):
        self.k_factor = k_factor
        self.candidates: Dict[str, VerifiedCandidate] = {}

    def register_candidate(self, candidate: VerifiedCandidate) -> None:
        if not candidate.signature_valid:
            raise ValueError(f"Rejected candidate {candidate.candidate_id}: invalid Ed25519 attestation.")
        self.candidates[candidate.candidate_id] = candidate

    @staticmethod
    def _cosine_alignment(vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
        shared_keys = set(vec_a.keys()) & set(vec_b.keys())
        if not shared_keys:
            return 0.0
        dot = sum(vec_a[k] * vec_b[k] for k in shared_keys)
        norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
        norm_b = math.sqrt(sum(v * v for v in vec_b.values()))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return round(dot / (norm_a * norm_b), 4)

    def route(self, query: EmployerQuery) -> List[MatchResult]:
        """Ranks verified candidates strictly by attested cartridge Elo and vector alignment."""
        ranked: List[MatchResult] = []

        for cand in self.candidates.values():
            if not cand.signature_valid:
                continue

            cand_elo = cand.verified_elos.get(query.required_cartridge, 0)
            if cand_elo < query.min_elo:
                continue

            alignment = self._cosine_alignment(cand.skill_vector, query.domain_weights)
            elo_surplus = min((cand_elo - query.min_elo) / 400.0, 1.0)

            raw_score = ((0.65 * alignment) + (0.35 * elo_surplus)) * cand.outcome_multiplier
            ranked.append(
                MatchResult(
                    candidate_id=cand.candidate_id,
                    match_score=round(raw_score, 4),
                    verified_elo=cand_elo,
                    domain_alignment=alignment,
                    rationale={
                        "cartridge": query.required_cartridge,
                        "elo_surplus": cand_elo - query.min_elo,
                        "outcome_multiplier": cand.outcome_multiplier,
                    },
                )
            )

        ranked.sort(key=lambda r: r.match_score, reverse=True)
        return ranked[: query.max_results]

    def record_trial_outcome(
        self,
        candidate_id: str,
        cartridge_id: str,
        trial_success_score: float,
        expected_score: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Closed-loop feedback: updates candidate Elo and routing trust multiplier
        based on post-match work trial performance (trial_success_score in [0.0, 1.0]).
        """
        if candidate_id not in self.candidates:
            raise KeyError(f"Candidate {candidate_id} not found.")

        cand = self.candidates[candidate_id]
        current_elo = cand.verified_elos.get(cartridge_id, 1500)
        expected = expected_score if expected_score is not None else 0.70

        delta = round(self.k_factor * (trial_success_score - expected))
        new_elo = max(800, current_elo + delta)
        cand.verified_elos[cartridge_id] = new_elo

        # Adjust outcome multiplier bounded within [0.75, 1.25]
        cand.outcome_multiplier = round(
            max(0.75, min(1.25, cand.outcome_multiplier + 0.05 * (trial_success_score - expected))),
            4,
        )

        return {
            "candidate_id": candidate_id,
            "cartridge_id": cartridge_id,
            "previous_elo": current_elo,
            "new_elo": new_elo,
            "updated_outcome_multiplier": cand.outcome_multiplier,
        }
