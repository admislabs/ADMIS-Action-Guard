from __future__ import annotations

import argparse
import json
import sys

from .decision import DecisionReceipt


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="admis", description="ADMIS Security SDK preview CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    verify = sub.add_parser("verify", help="Verify a demo decision receipt")
    verify.add_argument("receipt_path", help="Path to receipt JSON")
    verify.add_argument("--secret", default="admis-preview-secret", help="Preview HMAC verification secret")

    inspect = sub.add_parser("inspect", help="Inspect a demo decision receipt")
    inspect.add_argument("receipt_path", help="Path to receipt JSON")

    args = parser.parse_args(argv)

    if args.command == "verify":
        receipt = DecisionReceipt.load(args.receipt_path)
        ok = receipt.verify(secret=args.secret)
        print("Signature: valid" if ok else "Signature: invalid")
        print(f"Decision: {receipt.outcome}")
        print(f"Policy: {receipt.policy}@{receipt.policy_version}")
        print(f"Context hash: {receipt.context_hash}")
        return 0 if ok else 2

    if args.command == "inspect":
        receipt = DecisionReceipt.load(args.receipt_path)
        print(json.dumps(receipt.to_dict(), indent=2, sort_keys=True))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
