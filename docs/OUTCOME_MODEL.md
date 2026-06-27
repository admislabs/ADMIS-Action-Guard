# Canonical ADMIS Outcome Model

| Outcome | Meaning | Tool execution |
|---|---|---|
| ALLOW | Execute normally | Yes |
| ALLOW_WITH_LOGGING | Execute with elevated audit record | Yes |
| ALLOW_WITH_CONSTRAINTS | Execute only with narrowed scope or constraints | Conditional |
| STEP_UP_AUTH | Require stronger identity proof | No until completed |
| ESCALATE | Require human or policy-owner approval | No until approved |
| QUARANTINE | Isolate the agent, session, or action | No |
| BLOCK | Deny the proposed action | No |
| EMERGENCY_ABORT | Terminate execution and trigger incident workflow | No |
| REQUIRE_CONTEXT | Missing authority, scope, evidence, or policy context | No |

## Why this matters

Security buyers will inspect the semantics. Avoid mixing synonymous outcomes such as `deny` and `block` unless they are operationally distinct.

## Recommended language

Use **block** for a normal denied action. Use **emergency abort** only for critical conditions such as identity impersonation on an admin or transactional surface.
