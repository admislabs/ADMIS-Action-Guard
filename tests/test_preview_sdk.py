from admis import AdmisClient


def test_block_untrusted_agent():
    admis = AdmisClient(mode="enforce", policy="demo_default")
    decision = admis.check_action(
        action="data.read",
        agent_id="agent://unknown",
        trust_level=0.1,
        auth_strength="mfa",
        data_class="restricted",
    )
    assert decision.outcome.value == "BLOCK"
    assert decision.receipt.verify()


def test_guard_tool_quarantine():
    admis = AdmisClient(mode="enforce", policy="demo_strict")

    def export(destination):
        return "executed"

    safe_export = admis.guard_tool(
        export,
        action="data.export",
        resource="customer_records",
        trust_level=0.8,
        data_class="confidential",
        destination="external_bucket",
    )
    result = safe_export(destination="external_bucket")
    assert result.executed is False
    assert result.decision.outcome.value == "QUARANTINE"
