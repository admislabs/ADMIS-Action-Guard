from __future__ import annotations

from .decision import DecisionReceipt


def verify_receipt(path: str, secret: str = "admis-preview-secret") -> bool:
    receipt = DecisionReceipt.load(path)
    return receipt.verify(secret=secret)
