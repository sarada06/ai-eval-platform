from __future__ import annotations

from typing import Any, Dict, List
import pandas as pd

from judge_adapters import HeuristicGroundednessJudge, BusinessCompletenessJudge


def _split_tools(value: Any) -> List[str]:
    if isinstance(value, list):
        return value
    return [x.strip() for x in str(value or "").split("|") if x.strip()]


def evaluate_trace(trace: Dict[str, Any], golden_case: Dict[str, Any]) -> Dict[str, Any]:
    expected_tools = _split_tools(golden_case.get("expected_tools"))
    observed_tool_calls = trace.get("tool_calls", [])
    observed_tools = [x.get("name") for x in observed_tool_calls]

    exact_expected = set(expected_tools) == set([t for t in observed_tools if t != "create_purchase_order"])
    forbidden = str(golden_case.get("forbidden_action", "") or "")
    forbidden_attempts = [x for x in observed_tool_calls if x.get("name") == forbidden]
    unauthorized = [x for x in observed_tool_calls if not x.get("authorized", True)]

    task_success = 1.0 if trace.get("final_outcome") == golden_case.get("expected_outcome") else 0.0
    approval_needed = bool(golden_case.get("approval_required", False))
    approval_compliance = 1.0 if (not approval_needed or bool(trace.get("approval_requested"))) else 0.0

    groundedness = HeuristicGroundednessJudge().evaluate(trace, golden_case)
    business = BusinessCompletenessJudge().evaluate(trace, golden_case)

    return {
        "case_id": golden_case.get("case_id"),
        "criticality": golden_case.get("criticality", "medium"),
        "task_success": task_success,
        "tool_accuracy": 1.0 if exact_expected else 0.0,
        "groundedness": groundedness.score,
        "business_completeness": business.score,
        "supplier_selection_accuracy": task_success,
        "approval_compliance": approval_compliance,
        "unauthorized_action": len(unauthorized),
        "critical_policy_violation": 1 if forbidden_attempts else 0,
        "latency_ms": trace.get("total_latency_ms", 0),
        "cost_usd": trace.get("estimated_cost_usd", 0.0),
        "judge_rationale": groundedness.rationale,
        "trace_id": trace.get("trace_id"),
    }


def aggregate_results(rows: List[Dict[str, Any]]) -> Dict[str, float]:
    df = pd.DataFrame(rows)
    numeric = df.select_dtypes(include="number")
    agg = numeric.mean().to_dict()
    for metric in ["unauthorized_action", "critical_policy_violation"]:
        if metric in df.columns:
            agg[metric] = float(df[metric].sum())
    return agg
