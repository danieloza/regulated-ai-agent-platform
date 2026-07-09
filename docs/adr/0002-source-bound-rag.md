# ADR 0002: Source-Bound RAG

## Status

Accepted

## Context

Answers in a regulated setting must be attributable to approved material. Retrieval alone is not a trust boundary: indexed documents can contain prompt injection, secret-exfiltration requests, stale policy, or instructions that conflict with system controls. Generating an unsupported answer would reduce auditability and could present model inference as approved policy.

## Decision

The assistant retrieves indexed chunks and returns their document and chunk identifiers as citations. When no relevant approved context is found, it returns the safe response `I don't know based on the approved sources.` Retrieved documents are always treated as untrusted data, never as executable instructions.

The backend applies policy classification before retrieval and checks generated source text for injection and exfiltration patterns before returning it. Suspicious retrieved content produces a bounded warning instead of repeating the embedded instruction. Audit events retain the policy decision, selected citations, source-bound flag, workflow trace, and final answer.

## Consequences

- Answers have a traceable relationship to indexed evidence.
- Missing evidence fails closed with an explicit lack-of-knowledge response.
- Malicious document text cannot grant tool, shell, database, secret, or network access.
- Deterministic retrieval and policy behavior make security cases repeatable in tests.
- Source binding can reduce answer coverage when the corpus is incomplete or retrieval thresholds are conservative.
- Pattern-based controls and deterministic embeddings demonstrate the boundary but require stronger retrieval, content governance, and model-layer defenses for production use.

## Operational Notes

Run the security evaluation suite after policy, retrieval, chunking, or corpus-ingestion changes. Track citation coverage and safe no-answer rates separately from answer relevance. Production ingestion should add document provenance, access control, versioning, malware scanning, and review workflows without allowing document content to alter runtime policy.
