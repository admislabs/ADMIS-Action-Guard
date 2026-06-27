from __future__ import annotations

from typing import Any, Callable

from .client import AdmisClient


def guard_tool(client: AdmisClient, tool: Callable[..., Any], **kwargs: Any):
    """Functional helper around AdmisClient.guard_tool."""
    return client.guard_tool(tool, **kwargs)


def guard_agent(client: AdmisClient, agent: Any, **kwargs: Any):
    """Functional helper around AdmisClient.guard_agent."""
    return client.guard_agent(agent, **kwargs)
