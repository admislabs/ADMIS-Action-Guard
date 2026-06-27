# ADMIS Action Guard Preview v0.1 Package Manifest

This is the first private SDK drop. It should be sent as **ADMIS Action Guard Preview v0.1**.

## Included

### Core SDK

- `admis/client.py`: `AdmisClient`, `check_action()`, `guard_tool()`, `guard_agent()`
- `admis/decision.py`: canonical outcome model, decision object, guarded result, receipt object
- `admis/policy.py`: sanitized demo policy evaluator
- `admis/receipts.py`: receipt exports
- `admis/cli.py`: local receipt verification CLI
- `admis/integrations/`: adapter scaffolding for LangChain, LangGraph, MCP, and CrewAI

### Sanitized policy packs

- `policies/demo_default.yml`
- `policies/demo_strict.yml`
- `policies/demo_finance.yml`
- `policies/demo_healthcare.yml`

### Five hero threat scenarios

- `examples/01_guard_tool_data_exfiltration.py`
- `examples/02_guard_tool_admin_impersonation.py`
- `examples/03_guard_agent_multi_signal_threat.py`
- `examples/04_guard_tool_untrusted_agent.py`
- `examples/05_guard_agent_autonomous_finance.py`

### Documentation

- `docs/WRAPPER_REFACTOR_SPEC.md`
- `docs/OUTCOME_MODEL.md`

### Tests and packaging

- `tests/test_preview_sdk.py`
- `pyproject.toml`
- `README.md`

