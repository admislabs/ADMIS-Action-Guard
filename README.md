# ADMIS Action Guard Preview v0.1

**Pre-execution authorization for AI agent tool calls.**

ADMIS Action Guard is the first private SDK preview from the ADMIS LABS SDK. It lets developers wrap agent tools so proposed actions can be evaluated before execution.

```text
1. Agent proposes action
2. ADMIS Action Guard intercepts the tool call
3. Policy evaluates identity, scope, risk signals, data class, destination, and context
4. Decision Outcomes: ALLOW / CONSTRAIN / STEP-UP / ESCALATE / QUARANTINE / BLOCK / ABORT
5. Tool executes or is stopped
6. Decision receipt is issued
```

## What this first drop includes

- Native Python SDK surface
- `AdmisClient`
- `check_action()`
- `guard_tool()`
- `guard_agent()` preview hook
- Observe, simulate, and enforce modes
- Canonical nine-outcome decision model
- Decision receipts and local verification
- Sanitized demo policy packs
- Five hero threat-scenario examples
- Adapter scaffolding for agent frameworks under `admis/integrations/`
- Basic tests

## What this first drop does not include

- Hosted Risk Bridge
- Risk engine
- Production SIEM, IAM, OAuth, or PKI connectors
- Enterprise policy registry
- Approval workflows
- Full ADMIS Control Plane
- Production thresholds, weights, or proprietary scoring logic

## Install locally

From this directory:

```bash
python -m pip install -e .
```

No external dependencies are required for the preview examples.

## Quickstart

```python
from admis import AdmisClient

admis = AdmisClient(mode="enforce", policy="demo_strict")

safe_tool = admis.guard_tool(
    tool=export_customers,
    action="data.export",
    resource="customer_records",
    data_class="confidential",
    destination="external_bucket"
)

result = safe_tool(destination="external_bucket")

print(result.executed)
print(result.decision.outcome.value)
print(result.decision.receipt.receipt_id)
```

## Run the five hero threat scenarios

```bash
python examples/01_guard_tool_data_exfiltration.py
python examples/02_guard_tool_admin_impersonation.py
python examples/03_guard_agent_multi_signal_threat.py
python examples/04_guard_tool_untrusted_agent.py
python examples/05_guard_agent_autonomous_finance.py
```

## Run tests

```bash
python -m pytest tests
```

If `pytest` is not installed, the examples can be run directly with Python.

## Outcome model

| Outcome | Meaning |
|---|---|
| `ALLOW` | Execute normally |
| `ALLOW_WITH_LOGGING` | Execute with elevated audit record |
| `ALLOW_WITH_CONSTRAINTS` | Execute with narrowed scope or constraints |
| `STEP_UP_AUTH` | Require stronger identity proof |
| `ESCALATE` | Require human or policy-owner approval |
| `QUARANTINE` | Isolate the agent, session, or action |
| `BLOCK` | Deny the proposed action |
| `EMERGENCY_ABORT` | Terminate execution and trigger incident workflow |
| `REQUIRE_CONTEXT` | Missing authority, scope, evidence, or policy context |

## Positioning

**ADMIS Action Guard Preview:** pre-execution authorization for AI agent tool calls.

**Category line:** the action firewall for agentic systems.

**Differentiation:** observability tells you what the agent did. ADMIS decides whether the agent is allowed to do it before it happens.