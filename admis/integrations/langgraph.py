from __future__ import annotations

from typing import Any, Callable

from admis import AdmisClient


class AdmisLangGraphGuard:
    """Preview adapter for LangGraph node/tool execution."""

    def __init__(self, client: AdmisClient, *, agent_id: str = "agent://langgraph"):
        self.client = client
        self.agent_id = agent_id

    def wrap_node(self, node_fn: Callable[..., Any], *, action: str, resource: str = "langgraph_node"):
        return self.client.guard_tool(
            node_fn,
            action=action,
            resource=resource,
            agent_id=self.agent_id,
            surface="langgraph_node",
        )
