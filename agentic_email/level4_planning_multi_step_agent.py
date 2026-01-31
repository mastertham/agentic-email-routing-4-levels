from __future__ import annotations
from typing import List, Literal
from .models import Email, ActionLog
from .tools import fake_llm_classify, fake_llm_summarize, tool_extract_entities, tool_generate_questions
from .memory import Memory

PlanStep = Literal["CLASSIFY", "EXTRACT_ENTITIES", "CHECK_MISSING_INFO", "SUMMARIZE", "ROUTE"]

def create_plan(email: Email) -> List[PlanStep]:
    """
    In real Level 4, the LLM produces an explicit plan.
    Here we mimic planning with a lightweight rule:
    - If security words appear -> prioritize classify + entities + route fast (skip long summary)
    - Otherwise standard plan.
    """
    text = (email.subject + " " + email.body).lower()
    if any(k in text for k in ["breach", "phishing", "malware", "security"]):
        return ["CLASSIFY", "EXTRACT_ENTITIES", "CHECK_MISSING_INFO", "ROUTE"]
    return ["CLASSIFY", "EXTRACT_ENTITIES", "CHECK_MISSING_INFO", "SUMMARIZE", "ROUTE"]


def handle_email_level4(email: Email) -> ActionLog:
    """
    Level 4: Agent first creates a plan (explicit).
    Then executes plan steps.
    Key difference vs Level 3:
    - separates "planning" vs "execution"
    - plan can change based on context/risk
    """
    memory = Memory()
    log = ActionLog(level="Level 4 - Planning agent (plan then execute)", steps=[])

    inbox_map = {
        "Sales": "sales@company.com",
        "Support": "support@company.com",
        "Billing": "billing@company.com",
        "Security": "security@company.com",
        "HR": "hr@company.com",
        "Unknown": "triage@company.com",
    }

    plan = create_plan(email)
    log.steps.append(f"plan -> {plan}")

    for step in plan:
        if step == "CLASSIFY":
            cls = fake_llm_classify(email)
            memory.write("classification", cls)
            log.steps.append(f"execute CLASSIFY -> {cls.route} (conf={cls.confidence})")

        elif step == "EXTRACT_ENTITIES":
            entities = tool_extract_entities(email)
            memory.write("entities", entities)
            log.steps.append(f"execute EXTRACT_ENTITIES -> {list(entities.keys()) or 'none'}")

        elif step == "CHECK_MISSING_INFO":
            cls = memory.read("classification")
            entities = memory.read("entities", {})
            info = tool_generate_questions(cls, entities)
            log.steps.append(f"execute CHECK_MISSING_INFO -> need_more_info={info.need_more_info}")
            if info.need_more_info:
                memory.write("pending_questions", info.questions)
                log.outputs = {
                    "classification": cls.model_dump(),
                    "need_more_info": True,
                    "questions": info.questions,
                    "memory_history": memory.history,
                }
                return log

        elif step == "SUMMARIZE":
            summ = fake_llm_summarize(email)
            memory.write("summary", summ)
            log.steps.append("execute SUMMARIZE -> done")

        elif step == "ROUTE":
            cls = memory.read("classification")
            routed_to = inbox_map.get(cls.route, "triage@company.com")
            memory.write("routed_to", routed_to)
            log.steps.append(f"execute ROUTE -> {routed_to}")

    cls = memory.read("classification")
    summ = memory.read("summary")
    log.outputs = {
        "classification": cls.model_dump() if cls else None,
        "summary": summ.model_dump() if summ else None,
        "routed_to": memory.read("routed_to"),
        "entities": memory.read("entities", {}),
        "plan": plan,
        "memory_history": memory.history,
    }
    return log
