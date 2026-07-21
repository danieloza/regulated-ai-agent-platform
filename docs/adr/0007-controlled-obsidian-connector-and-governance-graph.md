# ADR 0007: Controlled Obsidian Connector and Governance Graph

## Status

Accepted

## Context

Policy and control owners often author operational knowledge in Markdown workspaces such as Obsidian. Directly indexing a workstation vault would blur the boundary between draft notes and approved knowledge, inherit no reliable access policy, and allow path traversal, symlink, prompt-injection, time-of-check/time-of-use, and accidental-deletion risks. Reviewers also need to trace a published claim back to its authoring note without presenting analytical similarity as proven lineage.

## Decision

The platform treats Obsidian as an authoring plane and the Knowledge Control Center as the governance and publication plane. A backend connector scans only allowlisted roots and configured folders and tags. It persists a Preview Diff, stores its digest, and requires a separate apply decision. Apply rescans the vault, rejects drift, registers immutable sources, and creates approval-gated knowledge changes. It never publishes directly into RAG.

Deleted notes are tombstoned and routed to retention review. Operator deep links use the official `obsidian://open` URI. The governance graph combines connector, note, source, change, claim, release, and run nodes. Persisted lineage is authoritative; lexical run overlap is visibly marked as inferred.

## Consequences

- Draft authoring remains convenient while production knowledge keeps provenance and a human publication gate.
- Persisted previews make the reviewed change set attributable and resistant to post-review drift.
- Path allowlists, symlink rejection, scope filters, and scan limits reduce filesystem and denial-of-service risk.
- Deletion cannot silently remove published knowledge or bypass retention decisions.
- The graph makes source-to-release lineage inspectable and provides an accessible relationship table.
- Connector execution requires server-side access to a controlled vault replica and explicit operational ownership.
- Preview persistence uses database capacity and retains raw note snapshots until the configured retention process removes them.
- Inferred graph edges are useful review signals but cannot be treated as proof or authorization evidence.

## Operational Notes

Production deployments must set `OBSIDIAN_ALLOWED_ROOTS`; otherwise the connector fails closed. The mounted vault should be read-only and synchronized from an approved system of record with source ACLs. Operators must review previews within 30 minutes. Durable scheduling, retries, dead-letter handling, DLP/malware inspection, retention cleanup, and alerting remain deployment responsibilities. Enterprise preview and apply endpoints require tenant authentication, role separation, idempotency keys, and metadata-only integration events.
