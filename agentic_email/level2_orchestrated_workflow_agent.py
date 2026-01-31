from __future__ import annotations
from .models import Email, ActionLog
from .tools import fake_llm_classify, fake_llm_summarize, tool_generate_questions, tool_extract_entities
from .memory import Memory

def handle_email_level2(email: Email, memory: Memory | None = None) -> ActionLog:
    """
    Level 2: Still pre-defined steps, but adds:
    - guardrails + branching
    - asks for more info if low confidence/missing entities
    This is "workflow orchestration that feels agentic" but steps are fixed by developer.
    """
    memory = memory or Memory()
    log = ActionLog(level="Level 2 - Orchestrated workflow agent", steps=[])

    cls = fake_llm_classify(email)
    log.steps.append(f"classify -> {cls.route} (conf={cls.confidence})")

    entities = tool_extract_entities(email)
    log.steps.append(f"extract_entities -> {list(entities.keys()) or 'none'}")

    info = tool_generate_questions(cls, entities)
    if info.need_more_info:
        log.steps.append(f"request_more_info -> {len(info.questions)} questions")
        memory.write("pending_questions", info.questions)
        log.outputs = {
            "classification": cls.model_dump(),
            "need_more_info": True,
            "questions": info.questions,
        }
        return log

    summ = fake_llm_summarize(email)
    log.steps.append("summarize -> 1-liner")

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
        "entities": entities,
    }
    return log
