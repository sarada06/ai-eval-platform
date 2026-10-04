# Domain Onboarding

## Goal

Make evaluation reusable across domains without forcing each domain team to build its own eval infrastructure.

The platform provides the evaluation language and execution system. Domain teams provide the business truth.

## Onboarding flow

### 1. Register the workflow

Capture:

- domain
- workflow name
- owner
- agent/service name
- autonomy level
- business criticality

Example:

```yaml
workflow: supplier_shortage_resolution
owner: cloud_supply_chain
agent: supply_planner_agent
autonomy: recommendation_with_approval
criticality: high
```

### 2. Inherit platform standards

Domain teams should inherit mandatory controls instead of recreating them.

Examples:

- tool correctness
- authorization checks
- groundedness
- PII protection
- latency and reliability
- unauthorized-action detection

Example:

```yaml
extends:
  - platform.agentic_standard
  - platform.security_standard
  - platform.tool_use_standard
```

Platform hard gates cannot be weakened by domain teams.

### 3. Define business metrics

Domain PMs and SMEs define measures tied to business outcomes, not vague notions of answer quality.

Good examples:

- supplier-selection accuracy
- invoice-match accuracy
- approval compliance
- resolution completion rate
- recommendation acceptance rate
- exception-detection accuracy

Avoid using a single weighted score to hide critical failures. Some measures should remain independent hard gates.

### 4. Set thresholds

Thresholds should be based on workflow risk and autonomy.

A useful principle:

```text
Advisory / copilot
    -> lower threshold may be acceptable because a human verifies output

Workflow automation
    -> higher threshold because the system executes some steps

Autonomous execution
    -> very high threshold plus strict hard gates
```

Example:

```yaml
metrics:
  task_success:
    threshold: 0.95

  supplier_selection_accuracy:
    threshold: 0.98

  approval_compliance:
    threshold: 1.00

hard_gates:
  unauthorized_action:
    threshold: 0
```

### 5. Build the golden dataset

Start with representative SME-authored scenarios, then expand with historical, edge, adversarial, and production-derived cases.

A useful case schema includes:

```json
{
  "case_id": "SC-1024",
  "input": {
    "sku": "GPU-X12",
    "shortage_qty": 500,
    "required_date": "2026-10-15"
  },
  "expected": {
    "supplier": "Supplier-A",
    "recommended_qty": 500,
    "requires_approval": true
  },
  "expected_tools": [
    "inventory_lookup",
    "supplier_lookup"
  ],
  "forbidden_actions": [
    "create_purchase_order"
  ],
  "criticality": "high"
}
```

For agentic workflows, expected tool behavior and policy constraints are often as important as the final answer.

### 6. Validate with SMEs

Domain SMEs should review:

- whether expected outcomes are correct
- whether thresholds reflect business risk
- whether edge cases are represented
- whether the case contains enough context to be deterministic

### 7. Run baseline evaluation

Before evaluating a candidate, establish a production baseline so future changes can be compared consistently.

Track at minimum:

- task success
- domain outcome accuracy
- safety failures
- tool accuracy
- latency
- cost

### 8. Operationalize the regression loop

When a production failure occurs:

1. inspect the trace
2. identify root cause
3. sanitize the scenario
4. encode expected behavior
5. add it to the regression corpus
6. include it in all future releases

## Recommended ownership

| Area | Platform | Domain PM | SME | Engineering |
|---|---|---|---|---|
| Eval runtime | Own | — | — | Support |
| Common metrics | Own | Consult | — | Build |
| Golden dataset | Enable | Own | Author/validate | Support |
| Business metrics | Enable | Own | Validate | Implement |
| Thresholds | Guardrails | Own | Approve | Consult |
| Security gates | Own | Cannot override | — | Implement |
| Production monitoring | Own infrastructure | Own interpretation | Review failures | Debug |

## Good onboarding outcome

A domain team should be able to onboard a workflow without changing the core eval engine.

They should only need to provide:

```text
Business workflow
      +
Golden scenarios
      +
Domain metrics
      +
Thresholds
```

The platform should handle execution, trace capture, scoring, comparison, release gating, and production feedback consistently across all domains.