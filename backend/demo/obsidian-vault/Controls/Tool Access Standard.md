---
title: Tool Access Standard
owner: Platform Security
classification: internal
status: approved
source_type: standard
policy_domain: tool-governance
review_due: 2027-02-28
tags: [governed-ai, control]
---

# Tool Access Standard

AI agents must use scoped backend tools and must never receive shell access, direct database credentials, or unrestricted network capabilities.

Regulated write operations require a recorded human approval before the tool gateway can execute the requested change.

This standard implements the runtime boundary described in [[AI Assistant Governance]].
