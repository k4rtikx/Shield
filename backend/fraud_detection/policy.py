
from dataclasses import dataclass


@dataclass(frozen=True)
class FraudPolicy:
    review_threshold: int = 30
    decline_threshold: int = 70


DEFAULT_POLICY = FraudPolicy()


def evaluate_policy(risk_assessment, policy=DEFAULT_POLICY):
    score = risk_assessment["risk_score"]

    if not isinstance(score, int) or isinstance(score, bool):
        raise ValueError("Risk score must be an integer")

    if not 0 <= score <= 100:
        raise ValueError("Risk score must be between 0 and 100")

    if policy.review_threshold >= policy.decline_threshold:
        raise ValueError(
            "Review threshold must be lower than decline threshold"
        )

    if score >= policy.decline_threshold:
        decision = "decline"
    elif score >= policy.review_threshold:
        decision = "review"
    else:
        decision = "allow"

    return {
        "decision": decision,
        "risk_score": score,
        "policy_version": "1.0",
        "signals": list(risk_assessment.get("signals", [])),
    }
