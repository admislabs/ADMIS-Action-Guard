import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

"""Hero demo 02: Admin impersonation emergency abort.

An agent attempts to modify IAM roles while impersonating another identity.
ADMIS stops the action before execution.
"""
from admis import AdmisClient


def modify_iam_roles(role: str):
    return f"modified IAM role: {role}"


admis = AdmisClient(mode="enforce", policy="demo_strict")

safe_admin = admis.guard_tool(
    modify_iam_roles,
    action="modify_iam_roles",
    resource="iam_roles",
    agent_id="agent://compromised-admin",
    surface="admin",
    auth_strength="mfa",
    trust_level=0.60,
    data_class="restricted",
    metadata={"impersonation": True},
)

result = safe_admin(role="security-admin")

print("Executed:", result.executed)
print("Outcome:", result.decision.outcome.value)
print("Reason:", result.decision.reason)
print("Evidence:", result.decision.evidence)
print("Receipt:", result.decision.receipt.receipt_id)
