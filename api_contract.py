"""Illustrative service contract for turning the prototype into Eval-as-a-Service."""

OPENAPI_SNIPPET = {
    "POST /evals/run": {
        "request": {"workflow_id": "supply-shortage", "candidate_version": "agent-v2.3", "dataset_id": "golden-v4"},
        "response": {"run_id": "eval-123", "status": "completed"},
    },
    "GET /evals/{run_id}": {"response": {"metrics": {}, "case_results": [], "release_gate": "PASS|FAIL"}},
    "POST /regressions": {"request": {"trace_id": "trace-123", "case_id": "SC-003", "failure_reason": "wrong outcome"}},
}
