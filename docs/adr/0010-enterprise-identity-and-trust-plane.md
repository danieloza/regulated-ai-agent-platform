# ADR 0010: Enterprise Identity and Trust Plane

## Status

Accepted

## Context

Regulated actions cannot be authorized from browser state, an LLM prompt, or a role label supplied in a request body. The platform needs a verifiable link between corporate identity, tenant membership, effective role, authentication assurance, the requested action, and the exact payload reviewed by a human.

Static API credentials remain useful for narrowly scoped workloads, but they do not provide workforce identity, MFA evidence, or maker-checker separation.

## Decision

The `/api/v1` boundary accepts either a scoped workload API key or an OIDC JWT. OIDC validation requires a trusted JWKS key, asymmetric algorithm allowlist, expected issuer and audience, expiry and issued-at claims, a subject, tenant membership, and an explicit group/role mapping. The raw token is not persisted or returned.

Every sensitive request is re-authorized server-side against tenant, minimum role, and authentication assurance. Regulated writes require AAL2 and create an expiring approval bound to a canonical SHA-256 payload digest. The requester cannot approve the same payload. Break-glass grants require an AAL2 administrator, an incident reference, an independent subject, a narrow scope, and a maximum 30-minute lifetime.

Local `/api/trust/*` routes exist only to make the controls demonstrable without an external identity provider. Deployments must expose the protected `/api/v1/trust/*` surface to enterprise clients.

## Consequences

- Workforce actions carry attributable OIDC identity and MFA assurance.
- Workload credentials remain available for bounded service-to-service operations.
- Tenant and role checks are enforced by the API, not trusted from the UI.
- Human approval is cryptographically bound to the reviewed payload.
- Maker-checker and break-glass evidence can be exported from the audit trail.
- An enterprise deployment must configure an identity provider, group mappings, key rotation, and access-review ownership.
- Local demo actors are not a replacement for corporate IAM and must not be exposed as a production authorization surface.

## Operational Notes

Use `OIDC_ISSUER`, `OIDC_AUDIENCE`, and either `OIDC_JWKS_URL` or `OIDC_JWKS_JSON`. Keep the algorithm allowlist asymmetric. Map corporate groups through `OIDC_GROUP_ROLE_MAP`, and verify the configured tenant claim. Put static JWKS and API credential digests in a secret manager.

Monitor authentication failures, tenant mismatches, step-up failures, approval backlog, maker-checker violations, and active break-glass grants. Test key rotation and expired, wrong-audience, wrong-issuer, cross-tenant, and low-assurance tokens before rollout.
