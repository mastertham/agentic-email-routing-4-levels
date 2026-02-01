from __future__ import annotations
from .models import Email, ActionLog
from .tools import fake_llm_classify, fake_llm_summarize

def handle_email_level1(email: Email) -> ActionLog:
    """
    Level 1: Classic deterministic workflow.
    - Always do: classify -> summarize -> route
    - No looping, no self-correction, no tool choice.
    """
    log = ActionLog(level="Level 1 - RPA + AI action", steps=[])

    cls = fake_llm_classify(email)
    log.steps.append(f"classify -> {cls.route} (conf={cls.confidence})")

    summ = fake_llm_summarize(email)
    log.steps.append("summarize -> 1-liner")

    x = 2
    # deterministic routing table
    inbox_map = {
        "Sales": "sales@company.com",
        "Support": "support@company.com",
        "Billing": "billing@company.com",
        "Security": "security@company.com",
        "HR": "hr@company.com",
        "Unknown": "triage@company.com",
    }
    routed_to = inbox_map.get(cls.route, "triage@company.com")
    log.steps.append(f"route -> {routed_to}")

    log.outputs = {
        "classification": cls.model_dump(),
        "summary": summ.model_dump(),
        "routed_to": routed_to,
    }
    return log
