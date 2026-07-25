# Governed Code Assurance

Governed Code Assurance connects application-security findings to AI governance and release control without turning the platform into an autonomous code writer.

## Control Flow

1. Select the allowlisted repository and pin a full commit SHA.
2. Import bounded SARIF evidence. Portfolio mode uses deterministic fixtures.
3. Normalize findings and link the finding class to a modeled Security Twin path.
4. Require a different operator to approve or deny remediation.
5. Attach an artifact digest plus external build, test, and security-evaluation results.
6. Evaluate the validated candidate with the `code-assurance-v1` Release Assurance bundle.
7. Export the integrity-bound evidence pack.

## Authority Boundary

The platform has no repository credential, clone capability, shell, patch application function, or deployment token. Remediation approval authorizes validation of a proposed change; it does not apply code. A Release Assurance `GO` authorizes a separate delivery process; it does not deploy.

## Portfolio and Production Modes

The portfolio implementation uses fixed profiles so the workflow runs locally without paid services or source-code egress. A production adapter would replace fixtures with authenticated, signed SARIF from isolated CI while preserving the state machine, RBAC, idempotency, tenant boundary, and evidence contract.
