import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

"""Hero demo 05: Autonomous finance action with constraints.

An autonomous portfolio agent proposes a financial action. ADMIS allows only with
constraints and a decision receipt.
"""
from admis import AdmisClient


def rebalance_portfolio(strategy: str):
    return f"portfolio rebalanced with {strategy}"


admis = AdmisClient(mode="enforce", policy="demo_finance")

safe_rebalance = admis.guard_tool(
    rebalance_portfolio,
    action="trade.execute",
    resource="portfolio_allocation",
    agent_id="agent://portfolio-optimizer",
    actor_type="autonomous_agent",
    surface="api_call",
    auth_strength="hardware_backed",
    trust_level=0.78,
    data_class="financial",
    metadata={"human_in_loop": False},
)

result = safe_rebalance(strategy="low_volatility")

print("Executed:", result.executed)
print("Outcome:", result.decision.outcome.value)
print("Reason:", result.decision.reason)
print("Constraints:", result.decision.constraints)
print("Receipt verifies:", result.decision.receipt.verify())
