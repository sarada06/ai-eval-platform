# Production Evaluation

## Goal

Treat evaluation as a continuous production quality system rather than a one-time benchmark.

The same contracts used before release should continue to operate after deployment so teams can compare offline quality, canary behavior, and production outcomes using a consistent measurement model.

## Lifecycle

```text
Change
  |
  v
Offline Evaluation
  |
  v
Release Gate
  |
  v
Canary Deployment
  |
  v
Production Sampling
  |
  v
Quality + Safety + Business Metrics
  |
  v
Failure Analysis
  |
  v
Regression Corpus
  |
  +------> Future Evaluations
```

## Before production

Every meaningful change should trigger evaluation, including:

- model changes
- prompt changes
- orchestration changes
- tool additions or schema changes
- retrieval/index updates
- policy updates
- domain-rule changes

The candidate version is executed against versioned golden and regression datasets and compared with the current production baseline.

## What to measure

### AI quality

- task success
- groundedness
- retrieval quality
- tool-selection accuracy
- tool-argument accuracy
- trajectory efficiency
- answer completeness

### Safety and governance

- unauthorized actions
- approval bypasses
- policy violations
- PII or sensitive-data exposure
- access-control failures
- prompt-injection susceptibility

### Operational health

- latency
- reliability
- tool failures
- retry rate
- loop rate
- token usage
- cost per task

### Business outcomes

These should be defined by domain teams and tied to real workflow value. Examples:

- shortage-resolution accuracy
- invoice-match accuracy
- manual effort avoided
- time to resolution
- exception rate
- human acceptance rate
- first-pass completion rate

## Baseline comparison

Absolute thresholds alone are not enough. Each candidate should also be compared with the currently deployed baseline.

Example:

| Metric | Baseline | Candidate | Change |
|---|---:|---:|---:|
| Task success | 91% | 95% | +4 pp |
| Groundedness | 96% | 97% | +1 pp |
| Tool accuracy | 98% | 98% | 0 pp |
| P95 latency | 2.1 s | 2.6 s | +24% |
| Cost / task | $0.08 | $0.10 | +25% |
| Critical safety failures | 0 | 0 | 0 |

This allows product and engineering teams to make evidence-based tradeoffs across quality, latency, cost, and risk.

## Release policy

A typical release decision should combine:

1. mandatory platform hard gates
2. domain-specific acceptance thresholds
3. regression checks versus baseline
4. canary health signals

Example hard gate:

```text
Task success:             97%   PASS
Groundedness:             98%   PASS
Tool accuracy:            99%   PASS
Unauthorized actions:      1    FAIL

Overall release: BLOCKED
```

Critical policy or security failures should not be diluted by an aggregate score.

## Production sampling

After release, evaluate a representative sample of production traces. Sampling can be stratified by:

- workflow type
- domain
- customer/tenant class
- model version
- toolset version
- risk level
- latency band
- human escalation
- detected failures

Use deterministic checks broadly and reserve model-based judging for dimensions that require semantic interpretation.

## Trace lineage

Every production trace should be attributable to the configuration that produced it.

Recommended fields include:

```json
{
  "agent_version": "2.3",
  "model_version": "model-x",
  "prompt_version": "p17",
  "toolset_version": "mcp-4",
  "retrieval_version": "idx-22",
  "eval_pack_version": "supplier-resolution-1.4"
}
```

This makes it possible to determine what changed when quality moves.

## Failure-to-regression loop

Every meaningful production incident should be reviewed for promotion into the regression corpus.

```text
Production failure
      |
      v
Triage + root cause
      |
      v
Create sanitized eval case
      |
      v
Add expected behavior
      |
      v
Regression corpus
      |
      v
Every future release
```

The regression corpus becomes institutional memory for failures the organization does not want to repeat.

## Continuous improvement questions

Teams should be able to answer:

- Which workflows have the highest failure rate?
- Which failure classes are growing?
- Did a model or prompt change improve business outcomes?
- Are safety failures concentrated in a particular tool or workflow?
- Which production incidents are not yet covered by regression tests?
- Is quality improving without unacceptable cost or latency growth?

A mature eval platform turns these questions into dashboards and release evidence rather than ad hoc analysis.