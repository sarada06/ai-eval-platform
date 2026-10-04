from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class JudgeResult:
    score: float
    rationale: str
    judge_type: str


class JudgeAdapter:
    def evaluate(self, trace: Dict[str, Any], golden_case: Dict[str, Any]) -> JudgeResult:
        raise NotImplementedError


class HeuristicGroundednessJudge(JudgeAdapter):
    """Offline stand-in for an LLM-as-judge adapter.

    Production implementations can swap this with Azure OpenAI/OpenAI/other
    providers while preserving the same interface and rubric contract.
    """

    def evaluate(self, trace: Dict[str, Any], golden_case: Dict[str, Any]) -> JudgeResult:
        grounded = bool(trace.get("grounded", False))
        expected_tools = [x for x in str(golden_case.get("expected_tools", "")).split("|") if x]
        observed_tools = [x.get("name") for x in trace.get("tool_calls", [])]
        evidence_coverage = 1.0 if all(t in observed_tools for t in expected_tools) else 0.7
        score = 0.98 * evidence_coverage if grounded else 0.55 * evidence_coverage
        return JudgeResult(
            score=round(score, 2),
            rationale=(
                "Answer is grounded in the expected tool evidence."
                if grounded else
                "Answer outcome conflicts with the available tool evidence or golden expectation."
            ),
            judge_type="heuristic_llm_judge_adapter",
        )


class BusinessCompletenessJudge(JudgeAdapter):
    def evaluate(self, trace: Dict[str, Any], golden_case: Dict[str, Any]) -> JudgeResult:
        expected = str(golden_case.get("expected_outcome", ""))
        observed = str(trace.get("final_outcome", ""))
        score = 1.0 if expected == observed else 0.4
        return JudgeResult(
            score=score,
            rationale="Observed business outcome matches golden truth." if score == 1.0 else "Observed business outcome differs from golden truth.",
            judge_type="business_rubric_adapter",
        )
