from __future__ import annotations
from typing import Literal
from .models import Email, ActionLog
from .tools import fake_llm_classify, fake_llm_summarize, tool_extract_entities, tool_generate_questions
from .memory import Memory

Decision = Literal["Classify", "ExtractEntities", "Summarize", "AskMoreInfo", "Route", "Stop"]

def decide_next_step(memory: Memory) -> Decision:
    """
    This mimics an agent policy:
    - based on current state, decide which tool to run next
    In a real agent, this would be LLM reasoning + tool schema.
    Here we implement the same idea with deterministic logic.
    """
    cls = memory.read("classification")
    entities = memory.read("entities", {})
    asked = memory.read("asked_more_info", False)
    has_summary = memory.read("summary") is not None
    routed_to = memory.read("routed_to")

    if cls is None:
        return "Classify"
    if not entities:
        return "ExtractEntities"

    info = tool_generate_questions(cls, entities)
    if info.need_more_info and not asked:
        return "AskMoreInfo"

    if not has_summary:
        return "Summarize"
    if routed_to is None:
        return "Route"
    return "Stop"


def handle_email_level3(email: Email, max_steps: int = 8) -> ActionLog:
    """
    Level 3: Agent chooses tools dynamically and loops until done.
    Key difference vs Level 2:
    - developer does NOT hardcode full step order
    - we provide tools + stopping condition + step budget
    """
    memory = Memory()
    log = ActionLog(level="Level 3 - ReAct agent (tool choice + loop)", steps=[])

    inbox_map = {
        "Sales": "sales@company.com",
        "Support": "support@company.com",
        "Billing": "billing@company.com",
        "Security": "security@company.com",
        "HR": "hr@company.com",
        "Unknown": "triage@company.com",
    }

    for i in range(max_steps):
        decision = decide_next_step(memory)
        log.steps.append(f"step[{i+1}] decide -> {decision}")

        if decision == "Classify":
            cls = fake_llm_classify(email)
            memory.write("classification", cls)
            continue

        if decision == "ExtractEntities":
            entities = tool_extract_entities(email)
            memory.write("entities", entities)
            continue

        if decision == "AskMoreInfo":
            cls = memory.read("classification")
            entities = memory.read("entities", {})
            info = tool_generate_questions(cls, entities)
            memory.write("asked_more_info", True)
            memory.write("pending_questions", info.questions)
            log.outputs = {
                "classification": cls.model_dump(),
                "need_more_info": True,
                "questions": info.questions,
                "memory_history": memory.history,
            }
            return log

        if decision == "Summarize":
            summ = fake_llm_summarize(email)
            memory.write("summary", summ)
            continue

        if decision == "Route":
            cls = memory.read("classification")
            routed_to = inbox_map.get(cls.route, "triage@company.com")
            memory.write("routed_to", routed_to)
            continue

        if decision == "Stop":
            break

    cls = memory.read("classification")
    summ = memory.read("summary")
    routed_to = memory.read("routed_to")

    log.outputs = {
        "classification": cls.model_dump() if cls else None,
        "summary": summ.model_dump() if summ else None,
        "routed_to": routed_to,
        "entities": memory.read("entities", {}),
        "memory_history": memory.history,
    }
    return log
