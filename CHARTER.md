# Open Merit Protocol — Founding Charter

## 1. Purpose
The Open Merit Protocol (`open-merit-protocol`) is open-source, anti-capture infrastructure for adversarial skill verification and zero-credential builder routing. It replaces static, pedigree-based gatekeeping with deterministic, sandboxed proof of capability.

## 2. Core Invariants

### I. Zero Credential Fields
- **No Pedigree Proxies:** Core schemas (`skill_vector.json`, `employer_query.json`) strictly prohibit fields for university degrees, GPAs, past employer brand names, demographic markers, or institutional endorsements.
- **Capability Over Claims:** Routing and matching rely solely on cryptographically attested sandbox telemetry (`Ed25519` signed) and anonymized latent aptitude vectors.

### II. Local-First Privacy
- **Raw Data Never Leaves the Edge:** Local extractors (`local_agent/`) process browser history, local repositories, and telemetry strictly on the user's machine.
- **Vector-Only Export:** Only normalized, non-reversible aptitude weights leave the user's device, governed by user-controlled thresholds in `config.yaml`.

### III. Adversarial Integrity & Anti-Gaming
- **Dynamic Perturbations:** Static benchmarks are inevitably memorized or gamed. Every evaluation cartridge must inject mid-task perturbations (sensor dropouts, payload shifts, hidden contractual traps, latency spikes) scaled via adaptive Elo difficulty.
- **Deterministic Ground Truth:** Evaluation scoring must be reproducible inside isolated, non-networked sandboxes (`Dockerfile`).

### IV. Anti-Capture & Radical Forkability
- **Copyleft Protection:** Licensed under **AGPLv3** so that any hosted wrapper, SaaS matching engine, or proprietary modification offered over a network must remain open-source.
- **Modular Cartridges:** Anyone may author, audit, or fork domain cartridges (`cartridges/`) without central approval or gatekeeper fees.

## 3. Governance & Amendments
Any modification to these four Core Invariants requires public consensus and must preserve backward compatibility for self-sovereign cryptographic attestations.
