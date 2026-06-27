import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

"""Hero demo 03: Multi-signal threat block.

A suspicious overnight agent has multiple elevated threat signals. ADMIS blocks
before the tool call executes.
"""
from admis import AdmisClient


def run_batch_job():
    return "batch job completed"


admis = AdmisClient(mode="enforce", policy="demo_strict")

safe_batch = admis.guard_tool(
    run_batch_job,
    action="batch.execute",
    resource="production_jobs",
    agent_id="agent://overnight-runner",
    auth_strength="mfa",
    trust_level=0.55,
    data_class="confidential",
    signals={
        "anomaly": 0.9,
        "privilege_escalation": 0.8,
        "unauthorized_access": 0.7,
        "lateral_movement": 0.7,
    },
)

result = safe_batch()

print("Executed:", result.executed)
print("Outcome:", result.decision.outcome.value)
print("Reason:", result.decision.reason)
print("Constraints:", result.decision.constraints)
print("Receipt:", result.decision.receipt.receipt_id)
