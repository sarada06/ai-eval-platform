# Production Eval Platform — Reference Prototype

This Streamlit prototype shows how a central AI platform can expose **Eval-as-a-Service** to domain teams while keeping business truth domain-owned.

## What is implemented

- Domain onboarding and workflow registration
- Non-bypassable platform standards
- Domain-defined business metrics and thresholds
- Editable/uploadable golden datasets
- Mock MCP/tool runtime with full agent traces
- Deterministic tool, approval, policy and business validators
- Swappable judge-adapter interface (offline heuristic implementation included)
- Candidate vs baseline comparison
- Release gating
- Trace explorer with tool arguments/results
- Failure promotion into a persistent regression corpus
- Illustrative API/service contract

## Ownership model

**Platform team owns**
- Eval runtime and trace schema
- Common validators and judge adapters
- Security/policy hard gates
- Baseline comparison and release logic
- Production sampling and regression plumbing

**Domain teams own**
- Business workflows and criticality/autonomy classification
- Business-specific metrics and thresholds
- Golden cases and expected outcomes
- SME validation of failures and regression cases

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Demo modes

- `candidate`: one business-quality failure is intentionally injected for SC-003.
- `unsafe-demo`: also attempts an unauthorized `create_purchase_order` action to demonstrate a platform hard-gate failure.

## Core flow

```text
Golden case
   ↓
Agent invocation
   ↓
Mock MCP/tool calls
   ↓
Trace capture (model/prompt/toolset/tools/actions)
   ↓
Deterministic validators + judge adapters
   ↓
Metric aggregation
   ↓
Platform hard gates + domain thresholds + baseline comparison
   ↓
Release / canary decision
   ↓
Production/eval failure → regression corpus
```

## Files

- `app.py` — Streamlit product experience
- `eval_core.py` — trace schema and mock MCP runtime
- `evaluators.py` — deterministic and business evaluation logic
- `judge_adapters.py` — swappable judge interface
- `regression_store.py` — promote failures into regression corpus
- `api_contract.py` — illustrative service API
- `sample_golden_dataset.csv` — example domain dataset

## Production next steps

For a real deployment, replace the mock runtime and heuristic judge with the organization's actual agent endpoint, MCP/tool gateway, identity context, model provider, OTEL trace collector, data store, and CI/CD integration. Keep the contracts stable so domain eval packs remain portable across implementations.
