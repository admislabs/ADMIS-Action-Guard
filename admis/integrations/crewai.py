from __future__ import annotations

from typing import Any, Callable

from admis import AdmisClient


class AdmisCrewAIGuard:
    """Preview adapter for CrewAI-style tools and agents."""

    def __init__(self, client: AdmisClient, *, agent_id: str = "agent://crewai"):
        self.client = client
        self.agent_id = agent_id

    def wrap_tool(self, tool_fn: Callable[..., Any], *, action: str, resource: str = "crewai_tool"):
        return self.client.guard_tool(
            tool_fn,
            action=action,
            resource=resource,
            agent_id=self.agent_id,
            surface="crewai_tool",
        )

    def guard_agent(self, agent: Any) -> Any:
        return self.client.guard_agent(agent, policy=self.client.policy, enforce=self.client.mode == "enforce")
