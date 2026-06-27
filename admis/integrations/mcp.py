from __future__ import annotations

from typing import Any, Callable

from admis import AdmisClient


class AdmisMCPGuard:
    """Preview adapter for MCP-style tool routers.

    Production implementation should wrap MCP tool invocation at the server or
    client boundary so every tool call carries action, resource, identity, and
    policy context.
    """

    def __init__(self, mcp_server: Any, *, client: AdmisClient, agent_id: str = "agent://mcp"):
        self.mcp_server = mcp_server
        self.client = client
        self.agent_id = agent_id

    def guard_callable(self, tool_fn: Callable[..., Any], *, tool_name: str, resource: str = "mcp_tool"):
        return self.client.guard_tool(
            tool_fn,
            action=f"mcp.{tool_name}",
            resource=resource,
            agent_id=self.agent_id,
            surface="mcp_tool_call",
        )
