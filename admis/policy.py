from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .decision import ActionRequest, Outcome


@dataclass(frozen=True)
class PolicyBundle:
    name: str
    version: str
    description: str
    demo_only: bool = True


POLICIES: Dict[str, PolicyBundle] = {
    "demo_default": PolicyBundle(
        name="demo_default",
        version="2026.06.preview",
        description="Balanced demo policy for non-production examples. Uses sanitized illustrative bands.",
    ),
    "demo_strict": PolicyBundle(
        name="demo_strict",
        version="2026.06.preview",
        description="Strict demo policy for sensitive agent actions. Uses sanitized illustrative bands.",
    ),
    "demo_finance": PolicyBundle(
        name="demo_finance",
        version="2026.06.preview",
        description="Finance-oriented demo policy for autonomous actions and transaction governance.",
    ),
    "demo_healthcare": PolicyBundle(
        name="demo_healthcare",
        version="2026.06.preview",
        description="Healthcare-oriented demo policy for sensitive data movement and access governance.",
    ),
}


HIGH_RISK_ACTION_HINTS = (
    "export",
    "delete",
    "transfer",
    "trade",
    "execute",
    "modify_iam",
    "admin",
    "database.write",
    "shell.execute",
    "credential",
    "secret",
)

SENSITIVE_DATA_CLASSES = {"confidential", "restricted", "regulated", "phi", "pii", "financial"}
EXTERNAL_DESTINATIONS = {"external_bucket", "external_domain", "public_internet", "unknown_destination"}
WEAK_AUTH = {"none", "unknown", "password_only", "api_key_only"}
ADMIN_SURFACES = {"admin", "iam", "root", "security_console"}
AUTONOMOUS_ACTORS = {"autonomous_agent", "agent"}


def evaluate_policy(request: ActionRequest, policy_name: str) -> Tuple[Outcome, str, str, List[str], List[Dict[str, str]]]:
    """Evaluate a proposed action with sanitized preview logic.

    This is intentionally not the production risk model. It demonstrates the
    SDK control surface while keeping real thresholds, weights, and policy
    calibration out of the public preview.
    """
    policy = POLICIES.get(policy_name, POLICIES["demo_default"])
    evidence: List[Dict[str, str]] = []
    constraints: List[str] = []

    action_lower = request.action.lower()
    resource_lower = (request.resource or "").lower()
    surface_lower = request.surface.lower()
    destination = (request.destination or "").lower()
    auth = request.auth_strength.lower()
    data_class = request.data_class.lower()
    trust = request.trust_level
    signals = {k.lower(): v for k, v in request.signals.items()}

    risk_points = 0

    def add(points: int, source: str, detail: str):
        nonlocal risk_points
        risk_points += points
        evidence.append({"source": source, "detail": detail, "demo": "true"})

    if trust is None:
        constraints.append("missing_trust_context")
        add(2, "context", "trust context missing")
    elif trust < 0.25:
        constraints.append("untrusted_agent")
        add(5, "identity", "agent trust is in demo low-trust band")
    elif trust < 0.55:
        constraints.append("low_agent_trust")
        add(3, "identity", "agent trust requires scrutiny")

    if auth in WEAK_AUTH:
        constraints.append("weak_authentication")
        add(3, "identity", "authentication strength requires step-up")

    if data_class in SENSITIVE_DATA_CLASSES:
        add(2, "data", f"{data_class} data class")

    if destination in EXTERNAL_DESTINATIONS:
        constraints.append("external_destination")
        add(4, "data_movement", "external or unknown destination")

    if any(hint in action_lower or hint in resource_lower for hint in HIGH_RISK_ACTION_HINTS):
        add(3, "action", "high-risk action family")

    if surface_lower in ADMIN_SURFACES:
        constraints.append("admin_surface")
        add(4, "surface", "administrative surface")

    if request.metadata.get("impersonation") is True:
        constraints.append("identity_impersonation")
        add(7, "identity", "identity impersonation detected")

    if request.actor_type.lower() in AUTONOMOUS_ACTORS and request.metadata.get("human_in_loop") is False:
        constraints.append("autonomous_execution")
        add(2, "agent_classification", "autonomous execution without human in loop")

    signal_flags = [name for name, value in signals.items() if value >= 0.5]
    if signal_flags:
        constraints.extend([f"signal:{name}" for name in signal_flags])
        add(2 * len(signal_flags), "signals", f"demo signal band elevated: {', '.join(signal_flags)}")

    # Critical deterministic conditions. These preserve semantics without
    # disclosing production thresholds or weights.
    if "identity_impersonation" in constraints and "admin_surface" in constraints:
        return Outcome.EMERGENCY_ABORT, "critical", "Identity impersonation on an administrative surface.", constraints, evidence

    if "untrusted_agent" in constraints:
        return Outcome.BLOCK, "critical", "Agent identity does not meet trust requirements.", constraints, evidence

    if "external_destination" in constraints and data_class in SENSITIVE_DATA_CLASSES:
        return Outcome.QUARANTINE, "high", "Sensitive data movement to external or unknown destination.", constraints, evidence

    if len(signal_flags) >= 3:
        return Outcome.BLOCK, "high", "Multiple independent threat signals are elevated.", constraints, evidence

    if "weak_authentication" in constraints:
        return Outcome.STEP_UP_AUTH, "medium", "Stronger authentication is required before execution.", constraints, evidence

    if "missing_trust_context" in constraints:
        return Outcome.REQUIRE_CONTEXT, "medium", "Required authority or trust context is missing.", constraints, evidence

    if "admin_surface" in constraints or "autonomous_execution" in constraints:
        return Outcome.ALLOW_WITH_CONSTRAINTS, "medium", "Action may proceed only with narrowed scope and audit logging.", constraints, evidence

    if risk_points >= 6:
        return Outcome.ESCALATE, "medium", "Risk signals require human or policy-owner review.", constraints, evidence

    if risk_points >= 3:
        return Outcome.ALLOW_WITH_LOGGING, "low", "Action is allowed with elevated audit logging.", constraints, evidence

    return Outcome.ALLOW, "low", "Action is admissible under the selected demo policy.", constraints, evidence
