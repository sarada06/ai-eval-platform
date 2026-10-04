# Architecture

## Purpose

This reference architecture shows how a central AI platform can provide reusable evaluation capabilities to many domain teams without centralizing domain-specific business truth.

The platform owns the mechanics of evaluation: execution, trace capture, validators, judges, release gates, regression handling, and production monitoring. Domain teams own the business scenarios, expected outcomes, metrics, and thresholds that define what good looks like for a workflow.

## High-level architecture

```text
Domain Eval Pack
      +
Golden Dataset
      |
      v
Evaluation Runtime
      |
      v
Agent / Model Runtime
      |
      v
MCP / Tool Gateway
      |
      v
Trace Capture
      |
      +--------------------+
      |                    |
      v                    v
Deterministic          Judge Adapters
Validators             LLM / rubric based
      |                    |
      +---------+----------+
                |
                v
        Metric Aggregation
                |
      +---------+----------+
      |                    |
      v                    v
Platform Gates       Domain Gates
      |                    |
      +---------+----------+
                |
                v
       Release Decision
                |
                v
       Canary / Production
                |
                v
     Production Monitoring
                |
                v
     Regression Corpus
```

## Core components

### 1. Domain eval pack

A versioned configuration package that declares:

- inherited platform standards
- domain metrics
- business thresholds
- hard gates
- evaluator bindings
- dataset references

Example:

```yaml
name: supplier_shortage_resolution
version: 1.0
extends:
  - platform.agentic_standard
  - platform.security_standard

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

### 2. Golden dataset

The golden dataset represents business truth and should contain more than an input and expected answer. A production-grade case can include:

- user or workflow input
- expected business outcome
- expected tools
- expected tool arguments
- approval requirements
- forbidden actions
- policy constraints
- scenario criticality
- metadata for segmentation

### 3. Evaluation runtime

The runtime executes cases consistently and captures all relevant execution context so results are reproducible and explainable.

Typical trace metadata includes:

- model and version
- prompt version
- toolset version
- retrieval/index version
- domain eval pack version
- tool trajectory
- tool arguments and results
- final outcome
- latency and cost
- authorization and policy events

### 4. Deterministic validators

Use deterministic validators wherever correctness can be objectively checked. Typical examples:

- exact business outcome match
- schema validity
- tool-selection accuracy
- tool-argument correctness
- approval compliance
- forbidden-action detection
- authorization violations
- SQL or graph query validity

### 5. Judge adapters

Judge adapters evaluate fuzzy dimensions that are difficult to encode deterministically, such as:

- groundedness
- completeness
- relevance
- instruction adherence
- explanation quality

The adapter pattern keeps the platform independent of a specific model provider or evaluation vendor.

### 6. Release gate

The release gate combines three forms of evidence:

1. non-bypassable platform hard gates
2. domain-specific thresholds
3. candidate-versus-baseline regression comparison

Critical safety failures should not be averaged into an overall quality score. A single unauthorized production action can block a release even when all other quality metrics are high.

## Ownership model

| Capability | Platform team | Domain team |
|---|---|---|
| Eval runtime | Own | Consume |
| Trace schema | Own | Consume |
| Common validators | Own | Extend |
| Safety hard gates | Own | Cannot weaken |
| Golden datasets | Enable | Own |
| Business metrics | Framework | Own |
| Thresholds | Guardrails | Own within guardrails |
| Production sampling | Own infrastructure | Define interpretation |
| Failure triage | Support | Own business disposition |

## Production integration points

A production implementation would typically integrate with:

- agent orchestration/runtime
- MCP or API tool gateway
- identity and authorization layer
- model provider(s)
- retrieval services and knowledge stores
- OTEL-compatible telemetry pipeline
- data warehouse / observability store
- CI/CD system
- incident management system

The goal is to keep the eval contracts stable while allowing those implementation details to evolve.