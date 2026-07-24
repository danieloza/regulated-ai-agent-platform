# ADR 0012: Adversarial Release Assurance

## Status

Accepted

## Context

A regulated AI control can regress even when the application still builds and its happy-path tests pass. Policy changes may relax a prior decision, tool-scope changes may create an attack path, and an operational shortcut may remove maker-checker evidence from a regulated write. Reviewing these signals in separate dashboards leaves the release owner to assemble a GO / NO-GO decision manually.

## Decision

The platform persists a release assurance run for each candidate control bundle. The run evaluates a fixed server-side certification matrix covering historical policy replay, adversarial security evals, modeled attack paths, source-bound RAG, human approval, and rollback readiness. It records the baseline-to-candidate control diff, modeled blast radius, per-check evidence references, readiness score, and blocking findings.

Blocking failures force `no_go`; the API does not expose an override that can approve such a run. A candidate with all mandatory controls satisfied remains `approval_required` until a different operator records a maker-checker decision. A positive decision creates an HMAC-SHA256 integrity attestation bound to the exact run, evidence, candidate version, score, and reviewer.

The attestation authorizes only an external release pipeline. The Release Assurance Center cannot deploy workloads or mutate policy, IAM, credentials, knowledge, tools, or business data.

## Consequences

- Release owners get one explainable control decision instead of manually correlating independent dashboards.
- Permission relaxation, approval bypass, adversarial-eval regression, and modeled record reachability are visible before rollout.
- Blocking controls fail closed and cannot be approved through the application API.
- Maker-checker separation and a payload-bound integrity digest make the decision attributable and tamper-evident.
- A deterministic matrix is reproducible in local tests and portfolio demonstrations.
- The matrix proves configured scenarios and evidence contracts; it does not discover every dependency or guarantee production safety.
- HMAC key custody, rotation, and verifier distribution become operational responsibilities.

## Operational Notes

Set a minimum 32-character `RELEASE_ATTESTATION_KEY` from a secret manager and use a non-empty `RELEASE_ATTESTATION_KEY_ID` to identify the active verification key. Production attestation fails closed when either control is missing or the key is too short. Local development uses a process-ephemeral key, so its attestations are intentionally unsuitable for cross-process verification. Run the migration to revision `c9e7a4d51b20` before starting a production backend.

Integrate the enterprise `/api/v1/release-assurance` resources with corporate OIDC, CI/CD, an authoritative service catalog, policy registry, security-eval store, and deployment approvals. Validate the attestation in the external pipeline, resolve the candidate image and configuration to immutable digests, and preserve the attestation with deployment evidence. A GO decision is necessary evidence, not a substitute for environment-specific canary, monitoring, rollback, or incident response.
