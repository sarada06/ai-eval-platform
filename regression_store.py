from __future__ import annotations

from pathlib import Path
from typing import Dict, Any
import csv


REGRESSION_FILE = Path(__file__).with_name("regression_corpus.csv")
FIELDS = [
    "case_id", "scenario", "expected_outcome", "expected_tools",
    "approval_required", "forbidden_action", "criticality", "source_trace_id", "failure_reason"
]


def promote_case(case: Dict[str, Any], source_trace_id: str, failure_reason: str) -> str:
    exists = REGRESSION_FILE.exists()
    with REGRESSION_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not exists:
            writer.writeheader()
        row = {k: case.get(k, "") for k in FIELDS}
        row["source_trace_id"] = source_trace_id
        row["failure_reason"] = failure_reason
        writer.writerow(row)
    return str(REGRESSION_FILE)
