## Summary

<!-- What problem does this change solve? -->

## Engineering Decision

<!-- Explain the selected approach, alternatives considered, and tradeoffs. -->

## Governance and Security Impact

<!-- Cover policy, identity, tenant boundaries, approvals, tools, audit, data, and operational effects. Write "None" only after reviewing each area. -->

## Validation

- [ ] Backend tests pass: `cd backend && python -m pytest`
- [ ] Frontend build passes: `cd frontend && npm ci && npm run build`
- [ ] Compose configuration passes: `docker compose config --quiet`
- [ ] PostgreSQL profile configuration passes: `docker compose --profile postgres config --quiet`
- [ ] Diff passes: `git diff --check`
- [ ] Security regression coverage was added or is not required
- [ ] Browser behavior and relevant responsive states were checked, if applicable

## Operational and Documentation Checklist

- [ ] Configuration changes are documented without real secrets
- [ ] Schema changes include an Alembic migration and rollback considerations
- [ ] API examples, ADRs, threat model, or operations guidance were updated, if applicable
- [ ] `CHANGELOG.md`, demo media, and screenshots were updated for a significant user-visible change
- [ ] No generated artifacts, credentials, personal data, or local workstation paths were committed

## Evidence

<!-- Link test output, screenshots, replay results, or other review evidence. -->
