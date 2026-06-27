from __future__ import annotations

from typing import Any, Callable, Dict, Optional
import functools
import uuid

from .decision import ActionRequest, Decision, GuardedResult, Outcome, make_receipt
from .policy import POLICIES, evaluate_policy


class AdmisClient:
    """ADMIS Security SDK client.

    Modes:
    - observe: evaluate and log, but do not block execution
    - simulate: evaluate and do not execute wrapped tools
    - enforce: apply the ADMIS decision before execution
    """

    def __init__(
        self,
        *,
        mode: str = "simulate",
        policy: str = "demo_default",
        api_key: Optional[str] = None,
        tenant_id: Optional[str] = None,
        receipt_secret: str = "admis-preview-secret",
    ) -> None:
        if mode not in {"observe", "simulate", "enforce"}:
            raise ValueError("mode must be one of: observe, simulate, enforce")
        if policy not in POLICIES:
            raise ValueError(f"unknown policy '{policy}'. Available: {', '.join(POLICIES)}")
        self.mode = mode
        self.policy = policy
        self.api_key = api_key
        self.tenant_id = tenant_id
        self.receipt_secret = receipt_secret

    def check_action(
        self,
        *,
        action: str,
        agent_id: str,
        resource: Optional[str] = None,
        user_id: Optional[str] = None,
        actor_type: str = "agent",
        surface: str = "tool_call",
        auth_strength: str = "unknown",
        trust_level: Optional[float] = None,
        data_class: str = "unknown",
        destination: Optional[str] = None,
        tool_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        signals: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Decision:
        request = ActionRequest(
            action=action,
            agent_id=agent_id,
            resource=resource,
            user_id=user_id,
            actor_type=actor_type,
            surface=surface,
            auth_strength=auth_strength,
            trust_level=trust_level,
            data_class=data_class,
            destination=destination,
            tool_name=tool_name,
            context=context or {},
            signals=signals or {},
            metadata=metadata or {},
        )
        outcome, risk_band, reason, constraints, evidence = evaluate_policy(request, self.policy)
        decision_id = f"adm_dec_{uuid.uuid4().hex[:12]}"
        receipt = make_receipt(
            request=request,
            decision_id=decision_id,
            outcome=outcome,
            policy=self.policy,
            policy_version=POLICIES[self.policy].version,
            secret=self.receipt_secret,
        )
        allowed = outcome.should_execute() if hasattr(outcome, "should_execute") else outcome in {
            Outcome.ALLOW,
            Outcome.ALLOW_WITH_LOGGING,
            Outcome.ALLOW_WITH_CONSTRAINTS,
        }
        return Decision(
            decision_id=decision_id,
            outcome=outcome,
            allowed=allowed,
            mode=self.mode,
            policy=self.policy,
            policy_version=POLICIES[self.policy].version,
            reason=reason,
            risk_band=risk_band,
            constraints=constraints,
            evidence=evidence,
            receipt=receipt,
            demo_only=True,
        )

    def guard_tool(
        self,
        tool: Callable[..., Any],
        *,
        action: str,
        resource: Optional[str] = None,
        agent_id: str = "agent://preview",
        user_id: Optional[str] = None,
        actor_type: str = "agent",
        surface: str = "tool_call",
        auth_strength: str = "mfa",
        trust_level: Optional[float] = 0.75,
        data_class: str = "unknown",
        destination: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        signals: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Callable[..., GuardedResult]:
        """Wrap a callable so ADMIS evaluates before execution."""

        @functools.wraps(tool)
        def wrapper(*args: Any, **kwargs: Any) -> GuardedResult:
            dynamic_destination = kwargs.get("destination", destination)
            dynamic_context = dict(context or {})
            dynamic_context.update({"tool_args_preview": _preview(args), "tool_kwargs_keys": list(kwargs.keys())})
            decision = self.check_action(
                action=action,
                agent_id=agent_id,
                resource=resource,
                user_id=user_id,
                actor_type=actor_type,
                surface=surface,
                auth_strength=auth_strength,
                trust_level=trust_level,
                data_class=data_class,
                destination=dynamic_destination,
                tool_name=getattr(tool, "__name__", "tool"),
                context=dynamic_context,
                signals=signals or {},
                metadata=metadata or {},
            )

            if self.mode == "simulate":
                return GuardedResult(executed=False, value=None, decision=decision)

            if self.mode == "observe":
                value = tool(*args, **kwargs)
                return GuardedResult(executed=True, value=value, decision=decision)

            # enforce mode
            if decision.should_execute():
                value = tool(*args, **kwargs)
                return GuardedResult(executed=True, value=value, decision=decision)
            return GuardedResult(executed=False, value=None, decision=decision)

        return wrapper

    def guard_agent(self, agent: Any, *, policy: Optional[str] = None, enforce: Optional[bool] = None) -> Any:
        """Generic placeholder guard for agent runtimes.

        Framework-specific adapters should implement tool wrapping for the agent's
        native tool registry. This generic method attaches ADMIS metadata and
        returns the agent unchanged for preview ergonomics.
        """
        setattr(agent, "_admis_policy", policy or self.policy)
        setattr(agent, "_admis_mode", "enforce" if enforce else self.mode)
        return agent


def _preview(value: Any, max_chars: int = 120) -> str:
    text = repr(value)
    return text if len(text) <= max_chars else text[: max_chars - 3] + "..."

# Enum helper monkey patch avoided in favor of function-level explicitness.
