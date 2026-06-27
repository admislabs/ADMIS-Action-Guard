from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional
import hashlib
import hmac
import json
import time
import uuid


class Outcome(str, Enum):
    ALLOW = "ALLOW"
    ALLOW_WITH_LOGGING = "ALLOW_WITH_LOGGING"
    ALLOW_WITH_CONSTRAINTS = "ALLOW_WITH_CONSTRAINTS"
    STEP_UP_AUTH = "STEP_UP_AUTH"
    ESCALATE = "ESCALATE"
    QUARANTINE = "QUARANTINE"
    BLOCK = "BLOCK"
    EMERGENCY_ABORT = "EMERGENCY_ABORT"
    REQUIRE_CONTEXT = "REQUIRE_CONTEXT"


EXECUTABLE_OUTCOMES = {
    Outcome.ALLOW,
    Outcome.ALLOW_WITH_LOGGING,
    Outcome.ALLOW_WITH_CONSTRAINTS,
}


@dataclass(frozen=True)
class ActionRequest:
    """A proposed agent action before execution."""

    action: str
    agent_id: str
    resource: Optional[str] = None
    user_id: Optional[str] = None
    actor_type: str = "agent"
    surface: str = "tool_call"
    auth_strength: str = "unknown"
    trust_level: Optional[float] = None
    data_class: str = "unknown"
    destination: Optional[str] = None
    tool_name: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    signals: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_canonical_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        return _canonicalize(data)


@dataclass(frozen=True)
class DecisionReceipt:
    """Tamper-evident demo receipt for an ADMIS decision.

    This preview uses HMAC-SHA256 for local verification. Production Premium
    infrastructure should use stronger external timestamping and durable audit
    chaining where required.
    """

    receipt_id: str
    decision_id: str
    outcome: str
    issued_at_unix: float
    context_hash: str
    signature_algorithm: str
    signature: str
    policy: str
    policy_version: str
    demo_only: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def verify(self, secret: str = "admis-preview-secret") -> bool:
        payload = {
            "decision_id": self.decision_id,
            "outcome": self.outcome,
            "issued_at_unix": self.issued_at_unix,
            "context_hash": self.context_hash,
            "policy": self.policy,
            "policy_version": self.policy_version,
            "demo_only": self.demo_only,
        }
        expected = _sign(payload, secret)
        return hmac.compare_digest(expected, self.signature)

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, sort_keys=True)

    @classmethod
    def load(cls, path: str) -> "DecisionReceipt":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)


@dataclass(frozen=True)
class Decision:
    decision_id: str
    outcome: Outcome
    allowed: bool
    mode: str
    policy: str
    policy_version: str
    reason: str
    risk_band: str
    constraints: List[str] = field(default_factory=list)
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    receipt: Optional[DecisionReceipt] = None
    demo_only: bool = True

    def should_execute(self) -> bool:
        return self.outcome in EXECUTABLE_OUTCOMES

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["outcome"] = self.outcome.value
        return data


@dataclass(frozen=True)
class GuardedResult:
    executed: bool
    value: Any
    decision: Decision



def make_receipt(
    request: ActionRequest,
    decision_id: str,
    outcome: Outcome,
    policy: str,
    policy_version: str,
    secret: str = "admis-preview-secret",
) -> DecisionReceipt:
    context_hash = hashlib.sha256(
        json.dumps(request.to_canonical_dict(), sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    issued_at = time.time()
    payload = {
        "decision_id": decision_id,
        "outcome": outcome.value,
        "issued_at_unix": issued_at,
        "context_hash": context_hash,
        "policy": policy,
        "policy_version": policy_version,
        "demo_only": True,
    }
    return DecisionReceipt(
        receipt_id=f"adm_rec_{uuid.uuid4().hex[:12]}",
        decision_id=decision_id,
        outcome=outcome.value,
        issued_at_unix=issued_at,
        context_hash=context_hash,
        signature_algorithm="HMAC-SHA256-PREVIEW",
        signature=_sign(payload, secret),
        policy=policy,
        policy_version=policy_version,
        demo_only=True,
    )


def _sign(payload: Dict[str, Any], secret: str) -> str:
    body = json.dumps(_canonicalize(payload), sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()


def _canonicalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _canonicalize(v) for k, v in sorted(value.items())}
    if isinstance(value, list):
        return [_canonicalize(v) for v in value]
    if isinstance(value, tuple):
        return [_canonicalize(v) for v in value]
    if isinstance(value, Enum):
        return value.value
    return value
