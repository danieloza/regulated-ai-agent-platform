# Security Policy

## Supported Versions

Security fixes are applied to the current `main` branch and, when appropriate,
the latest published release. Earlier portfolio releases are not maintained as
separate long-lived support branches.

| Version | Supported |
| --- | --- |
| `main` | Yes |
| Latest release | Best effort |
| Older releases | No |

## Reporting a Vulnerability

Do not disclose suspected vulnerabilities, credentials, personal data, or
working exploit details in a public issue, discussion, pull request, or demo
artifact.

Use GitHub's private vulnerability reporting flow from the repository
**Security** tab. If that option is unavailable, contact the maintainer through
the [GitHub profile](https://github.com/danieloza) and request a private channel
before sharing technical details.

Include, where possible:

- affected commit, release, endpoint, or component;
- prerequisites and a minimal reproduction;
- expected and observed security behavior;
- potential effect on confidentiality, integrity, availability, tenant
  isolation, approvals, or audit evidence;
- suggested remediation or compensating control;
- whether the issue is already public or under active exploitation.

The maintainer will assess scope, severity, reproducibility, and disclosure
timing. This portfolio repository does not provide a contractual response SLA,
bug bounty, or production support commitment.

## Security Scope

Reports are especially useful when they involve:

- authentication, authorization, tenant isolation, or maker-checker bypass;
- policy bypass, prompt-injection escalation, or unsafe tool execution;
- secret, token, PII, or Secure Context disclosure;
- approval payload substitution, replay, or idempotency failure;
- evidence-pack integrity or audit-record tampering;
- unsafe document ingestion, path handling, or connector access;
- dependency, container, CI/CD, or release provenance compromise;
- denial of service that bypasses intended rate limits.

The deterministic demo credentials, mock data, local-only adapters, and
documented production limitations are not vulnerabilities by themselves.
However, a path that unexpectedly exposes them outside their documented
boundary should be reported.

## Coordinated Disclosure

Please allow reasonable time to reproduce and remediate a confirmed issue before
public disclosure. Avoid accessing data that is not yours, degrading shared
services, or using social engineering. Good-faith research that respects these
boundaries is welcomed.

For the platform's modeled threats and deployment assumptions, see
[docs/threat-model.md](docs/threat-model.md) and
[docs/production-limitations.md](docs/production-limitations.md).
