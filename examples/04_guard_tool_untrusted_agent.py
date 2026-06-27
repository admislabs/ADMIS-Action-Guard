import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

"""Hero demo 04: Untrusted agent identity block.

A low-trust agent attempts to access sensitive data. ADMIS blocks at the identity gate.
"""
from admis import AdmisClient


def access_sensitive_data(record_id: str):
    return {"record_id": record_id, "status": "read"}


admis = AdmisClient(mode="enforce", policy="demo_default")

safe_read = admis.guard_tool(
    access_sensitive_data,
    action="data.read",
    resource="sensitive_customer_record",
    agent_id="agent://unknown-service",
    auth_strength="mfa",
    trust_level=0.15,
    data_class="restricted",
)

result = safe_read(record_id="cust_123")

print("Executed:", result.executed)
print("Outcome:", result.decision.outcome.value)
print("Reason:", result.decision.reason)
print("Evidence:", result.decision.evidence)
