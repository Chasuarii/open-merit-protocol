import sqlite3
import shutil
import tempfile
from pathlib import Path
from typing import Dict
import json

# Raw URLs and domains stay strictly inside local memory; only vector weights are exported.
DOMAIN_TAXONOMY = {
    "robotics_controls": ["mujoco", "ros.org", "pid", "actuator", "kinematics", "embedded", "rust-embedded", "stm32"],
    "systems_architecture": ["kernel.org", "distributed", "raft", "ebpf", "llvm", "cuda", "latency", "concurrency"],
    "energy_thermodynamics": ["inverters", "lifepo4", "mppt", "heat-pump", "grid", "photovoltaic", "thermodynamics"],
    "regulatory_arbitrage": ["sec.gov", "ucc", "statute", "jurisdiction", "trust", "corporate-structure", "case-law"]
}

def extract_local_aptitude(history_db_path: Path) -> Dict[str, float]:
    """Reads local browser history safely and computes normalized curiosity/depth scores."""
    with tempfile.NamedTemporaryFile(delete=True) as tmp:
        shutil.copy2(history_db_path, tmp.name)
        conn = sqlite3.connect(tmp.name)
        cursor = conn.cursor()
        # Query visit counts and total dwell time (in microseconds for Chromium)
        cursor.execute("SELECT url, title, visit_count, typed_count FROM urls WHERE visit_count > 1")
        rows = cursor.fetchall()
        conn.close()

    raw_scores = {k: 0.0 for k in DOMAIN_TAXONOMY}
    for url, title, visits, typed in rows:
        text = f"{url} {title or ''}".lower()
        # Weight direct navigation / deep repeat visits higher than accidental clicks
        depth_weight = (visits * 1.0) + (typed * 2.5)
        for domain, keywords in DOMAIN_TAXONOMY.items():
            if any(kw in text for kw in keywords):
                raw_scores[domain] += depth_weight

    max_score = max(raw_scores.values()) or 1.0
    # Normalize to [0.0, 1.0] vector; zero raw URLs leave this function
    return {k: round(min(v / max_score, 1.0), 4) for k, v in raw_scores.items()}

if __name__ == "__main__":
    # Example Chromium default path; outputs anonymized vector ready for conversational router
    default_db = Path.home() / ".config/google-chrome/Default/History"
    if default_db.exists():
        print(json.dumps({"latent_aptitude": extract_local_aptitude(default_db)}, indent=2))
