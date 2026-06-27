from __future__ import annotations

from typing import Any, Iterable, List

from admis import AdmisClient


class AdmisToolGuard:
    """Thin preview adapter for LangChain-style tools.

    In production, this should preserve the native LangChain Tool interface.
    This preview demonstrates the integration shape without taking a dependency
    on LangChain.
    """

    def __init__(self, client: AdmisClient, *, agent_id: str = "agent://langchain", policy: str = "demo_default"):
        self.client = client
        self.agent_id = agent_id
        self.policy = policy

    def wrap_tool(self, tool: Any, *, action: str = "tool.call", resource: str = "langchain_tool") -> Any:
        callable_tool = getattr(tool, "func", tool)
        return self.client.guard_tool(
            callable_tool,
            action=action,
            resource=resource,
            agent_id=self.agent_id,
            surface="langchain_tool",
        )

    def wrap_tools(self, tools: Iterable[Any]) -> List[Any]:
        return [self.wrap_tool(t, action=f"tool.{getattr(t, 'name', getattr(t, '__name__', 'call'))}") for t in tools]


def guard_agent(agent: Any, *, client: AdmisClient, policy: str = "demo_default", enforce: bool = True) -> Any:
    return client.guard_agent(agent, policy=policy, enforce=enforce)
