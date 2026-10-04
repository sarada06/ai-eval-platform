from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
import time
import uuid


@dataclass
class ToolCall:
    name: str
    arguments: Dict[str, Any]
    result: Dict[str, Any]
    authorized: bool = True
    latency_ms: int = 0


@dataclass
class AgentTrace:
    trace_id: str
    case_id: str
    model: str
    prompt_version: str
    toolset_version: str
    final_outcome: str
    final_answer: str
    grounded: bool
    approval_requested: bool
    tool_calls: List[ToolCall]
    total_latency_ms: int
    estimated_cost_usd: float

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        return data


class MockMCPRuntime:
    """Small deterministic runtime that mimics MCP/tool execution for the prototype."""

    TOOL_LATENCY = {
        "inventory_lookup": 220,
        "supplier_lookup": 300,
        "lead_time_lookup": 180,
        "create_purchase_order": 350,
    }

    def call(self, tool_name: str, arguments: Dict[str, Any], authorized: bool = True) -> ToolCall:
        latency = self.TOOL_LATENCY.get(tool_name, 150)
        if not authorized:
            return ToolCall(tool_name, arguments, {"error": "unauthorized"}, False, latency)

        sample_results = {
            "inventory_lookup": {"available_qty": 0, "shortage_confirmed": True},
            "supplier_lookup": {
                "approved_suppliers": ["Supplier A", "Supplier B"],
                "capacity": {"Supplier A": 700, "Supplier B": 900},
                "moq": {"Supplier A": 100, "Supplier B": 250},
            },
            "lead_time_lookup": {"Supplier A": 10, "Supplier B": 18},
            "create_purchase_order": {"po_id": "PO-DEMO-001", "status": "created"},
        }
        return ToolCall(tool_name, arguments, sample_results.get(tool_name, {"ok": True}), True, latency)


def _expected_tools(case: Dict[str, Any]) -> List[str]:
    raw = case.get("expected_tools", "")
    if isinstance(raw, list):
        return raw
    return [x.strip() for x in str(raw).split("|") if x.strip()]


def simulate_agent_trace(case: Dict[str, Any], variant: str = "candidate") -> AgentTrace:
    """Generate a reproducible trace from a golden case.

    Candidate intentionally has one recoverable quality issue on SC-003 to show
    how case-level failures and regression promotion work.
    """
    runtime = MockMCPRuntime()
    expected_tools = _expected_tools(case)
    calls: List[ToolCall] = []

    for tool in expected_tools:
        calls.append(runtime.call(tool, {"case_id": case.get("case_id")}))

    expected_outcome = str(case.get("expected_outcome", "unknown"))
    final_outcome = expected_outcome
    grounded = True
    approval_requested = bool(case.get("approval_required", False))

    if variant == "candidate" and case.get("case_id") == "SC-003":
        final_outcome = "recommend_supplier_a"
        grounded = False

    if variant == "unsafe-demo" and case.get("case_id") == "SC-002":
        calls.append(runtime.call("create_purchase_order", {"qty": 500}, authorized=False))

    total_latency = 900 + sum(c.latency_ms for c in calls)
    cost = 0.045 + 0.009 * len(calls)
    answer = f"Outcome: {final_outcome}. Evidence derived from {', '.join([c.name for c in calls]) or 'no tools'}."

    return AgentTrace(
        trace_id=str(uuid.uuid4()),
        case_id=str(case.get("case_id")),
        model="gpt-enterprise-demo",
        prompt_version="p17",
        toolset_version="mcp-4",
        final_outcome=final_outcome,
        final_answer=answer,
        grounded=grounded,
        approval_requested=approval_requested,
        tool_calls=calls,
        total_latency_ms=total_latency,
        estimated_cost_usd=round(cost, 3),
    )


def run_cases(cases: List[Dict[str, Any]], variant: str = "candidate") -> List[AgentTrace]:
    return [simulate_agent_trace(case, variant=variant) for case in cases]
