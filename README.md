# open-merit-protocol
Open-source, anti-capture infrastructure for adversarial skill verification and zero-credential builder routing
# Open Merit Protocol (`open-merit-protocol`)

**Open-source, anti-capture infrastructure for adversarial skill verification and zero-credential builder routing.**

The Open Merit Protocol replaces static resumes, degree gatekeeping, and institutional brand proxies with deterministic, sandboxed proof of capability. Builders demonstrate real-world problem-solving under live adversarial perturbations inside offline containers, generating self-sovereign, cryptographically attested capability vectors.

---

## Core Principles

* **Zero Credential Fields:** Core schemas (`skill_vector.json`, `employer_query.json`) strictly prohibit university degrees, GPAs, past employer names, or demographic proxies.
* **Local-First Privacy:** On-device extractors (`local_agent/`) process browsing history and local telemetry strictly on your machine—raw URLs never leave your device.
* **Adversarial Integrity:** Static benchmarks get memorized. Every domain cartridge injects mid-task shocks (sensor dropouts, payload shifts, hidden contractual backdoors, latency spikes) scaled via adaptive Elo difficulty.
* **Anti-Capture Copyleft:** Licensed under **AGPLv3** so any hosted wrapper, SaaS matching engine, or network modification must remain open-source.

---

## Repository Architecture

```text
open-merit-protocol/
├── LICENSE                        # GNU Affero General Public License v3.0 (AGPLv3)
├── CHARTER.md                     # Founding governance invariants & protocol rules
├── docker-compose.yml             # Local vector DB + matching engine + sandbox runner
├── core/
│   ├── schemas/
│   │   ├── skill_vector.json      # Cryptographically signed Candidate Skill & Aptitude Graph
│   │   ├── employer_query.json    # Constraint-based matching schema (zero credential fields)
│   │   └── cartridge_spec.json    # Universal Domain Cartridge interface specification
│   └── engine/
│       ├── adversary.py           # Dynamic perturbation & Elo adaptive difficulty controller
│       ├── verifier.py            # Ed25519 cryptographic attestation signer & verifier
│       └── router.py              # Two-sided conversational matching & outcome feedback loop
├── local_agent/
│   ├── browser_extractor.py       # On-device privacy-preserving Aptitude Vector extractor
│   └── config.yaml                # Local-only privacy thresholds & domain taxonomy
└── cartridges/
    ├── robotics_control_v1/       # Robotics & embedded control loop sandbox (MuJoCo)
    └── contract_arbitrage_v1/     # Adversarial contract & structural risk defense sandbox
```

---

## Quick Start

### 1. Generate Your Local Aptitude Vector (On-Device)
Run the local extractor to compute normalized domain weights without exposing raw URLs:
```bash
python local_agent/browser_extractor.py
```
Customize excluded domains and visit thresholds inside `local_agent/config.yaml`.

### 2. Launch the Core Matching Engine & Vector DB
Start the local Qdrant vector store and zero-credential matching router:
```bash
docker compose up -d
```

### 3. Run an Isolated Cartridge Evaluation
Execute a domain cartridge inside an air-gapped (`network_mode: "none"`) sandbox:
```bash
docker compose --profile evaluation run --rm sandbox-robotics
```

---

## Contributing & Authoring Cartridges

Anyone can author, audit, or fork new domain cartridges under `cartridges/` without gatekeeper approval. Every cartridge must conform to `core/schemas/cartridge_spec.json` and include:
1. **`perturbations.json`** — Initial scenario state and multi-stage adversarial shocks.
2. **`evaluator.py`** — Deterministic ground-truth scoring logic.
3. **`Dockerfile`** *(for simulation/code cartridges)* — Reproducible, offline execution environment.

See [`CHARTER.md`](./CHARTER.md) for the protocol's non-negotiable invariants.

---

## License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPLv3)** — see the [`LICENSE`](./LICENSE) file for full details.
