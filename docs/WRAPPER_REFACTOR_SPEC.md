# Wrapper Refactor Spec

## Objective

Move ADMIS Security SDK from API-demo snippets to a native developer SDK that wraps agent tools and enforces admissibility before execution.

## Current gap

The initial examples show direct `httpx.post()` calls into local evaluation endpoints. That demonstrates the backend API, but it does not create a developer-native SDK wedge.

## Required SDK primitives

### `check_action()`

Evaluates a proposed agent action before execution.

### `guard_tool()`

Wraps a Python callable so ADMIS intercepts the action before the tool executes.

### `guard_agent()`

Attaches ADMIS guardrails to an agent runtime or framework-level tool registry.

### `DecisionReceipt`

Creates a tamper-evident record of the decision and the context hash.

## Required modes

| Mode | Purpose |
|---|---|
| observe | Log decisions but do not block execution |
| simulate | Show what would happen without executing the wrapped tool |
| enforce | Apply ADMIS decisions before execution |

## Required adapters

- LangChain tools
- LangGraph nodes
- MCP tool calls
- CrewAI tools
- Raw Python decorator/callable fallback

## Definition of done

A developer should be able to guard an existing tool in under five minutes without manually constructing JSON or calling an evaluation endpoint.
