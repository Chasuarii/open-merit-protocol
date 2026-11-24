import json
from pathlib import Path
from typing import Dict, Any, List

# Deterministic structural criteria (maps cleanly to LLM-as-a-Judge rubric or structured AST/clause rules)
REQUIRED_STRUCTURAL_DEFENSES = {
    "C1_IP_LICENSE": {
        "must_eliminate": ["perpetual license to derivatives", "weights ownership transfer"],
        "must_establish": ["strict customer IP retention", "zero training/weight rights for supplier"],
        "weight": 0.25
    },
    "C2_INDEMNITY_ASYMMETRY": {
        "must_eliminate": ["unlimited client liability", "1-month supplier cap"],
        "must_establish": ["mutual liability cap", "carve-out for supplier gross negligence/IP infringement"],
        "weight": 0.20
    },
    "C3_AUTO_RENEWAL_LOCK": {
        "must_eliminate": ["5-day certified mail trap window", "36-month lock-in"],
        "must_establish": ["termination for convenience with 30-day notice", "no penalty exit"],
        "weight": 0.15
    },
    "DEF_ROFR_BACKDOOR": {
        "must_eliminate": ["right of first refusal", "equity/asset encumbrance in definitions"],
        "must_establish": ["strike definition backdoor", "explicit anti-encumbrance clause"],
        "weight": 0.25
    },
    "PASS_THROUGH_FEE_EXPLOIT": {
        "must_eliminate": ["unilateral regulatory surcharge pass-through"],
        "must_establish": ["all-in fixed pricing", "immediate penalty-free termination upon any fee hike"],
        "weight": 0.15
    }
}

def evaluate_contract_defense(candidate_redlines: Dict[str, List[str]], reaction_time_sec: float) -> Dict[str, Any]:
    """
    Scores a candidate's structural counter-moves across all 5 adversarial stages.
    candidate_redlines maps trap_id -> list of structural defenses implemented.
    """
    earned_weight = 0.0
    missed_traps = []

    for trap_id, rules in REQUIRED_STRUCTURAL_DEFENSES.items():
        defenses = [d.lower() for d in candidate_redlines.get(trap_id, [])]
        matched = any(req in " ".join(defenses) for req in rules["must_establish"])
        if matched:
            earned_weight += rules["weight"]
        else:
            missed_traps.append(trap_id)

    # First-principles efficiency rewards catching all traps cleanly within the 45-min (2700s) window
    time_ratio = min(reaction_time_sec / 2700.0, 1.5)
    efficiency_score = max(0.0, round(1.0 - (0.35 * max(0.0, time_ratio - 0.5)), 4))
    recovery_score = 1.0 if ("DEF_ROFR_BACKDOOR" not in missed_traps and "PASS_THROUGH_FEE_EXPLOIT" not in missed_traps) else 0.35

    composite = round((0.60 * earned_weight) + (0.25 * recovery_score) + (0.15 * efficiency_score), 4)

    return {
        "cartridge_id": "risk.contract_arbitrage.v1",
        "composite_score": composite,
        "universal_traits": {
            "perturbation_recovery_pct": round(recovery_score * 100, 2),
            "first_principles_efficiency": round(efficiency_score * 100, 2)
        },
        "telemetry": {
            "structural_coverage_pct": round(earned_weight * 100, 2),
            "missed_traps": missed_traps,
            "completion_time_sec": reaction_time_sec
        }
    }

if __name__ == "__main__":
    # Test run demonstrating a sharp uncredentialed risk architect catching all 5 traps
    sample_submission = {
        "C1_IP_LICENSE": ["strict customer IP retention and zero training/weight rights for supplier"],
        "C2_INDEMNITY_ASYMMETRY": ["mutual liability cap with carve-out for supplier gross negligence/IP infringement"],
        "C3_AUTO_RENEWAL_LOCK": ["termination for convenience with 30-day notice and no penalty exit"],
        "DEF_ROFR_BACKDOOR": ["strike definition backdoor and add explicit anti-encumbrance clause"],
        "PASS_THROUGH_FEE_EXPLOIT": ["all-in fixed pricing with immediate penalty-free termination upon any fee hike"]
    }
    print(json.dumps(evaluate_contract_defense(sample_submission, reaction_time_sec=1420), indent=2))
