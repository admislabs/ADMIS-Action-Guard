import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

"""Hero demo 01: Data exfiltration prevention.

An agent attempts to export confidential customer records to an external bucket.
ADMIS intercepts the tool call before execution and quarantines the action.
"""
from admis import AdmisClient


def export_customers(destination: str):
    return f"exported customer records to {destination}"


admis = AdmisClient(mode="enforce", policy="demo_strict")

safe_export = admis.guard_tool(
    export_customers,
    action="data.export",
    resource="customer_records",
    agent_id="agent://etl-pipeline",
    auth_strength="mfa",
    trust_level=0.72,
    data_class="confidential",
    destination="external_bucket",
)

result = safe_export(destination="external_bucket")

print("Executed:", result.executed)
print("Outcome:", result.decision.outcome.value)
print("Reason:", result.decision.reason)
print("Constraints:", result.decision.constraints)
print("Receipt:", result.decision.receipt.receipt_id)
print("Receipt verifies:", result.decision.receipt.verify())
