from __future__ import annotations
from typing import List, Dict
from .models import Email, Classification, Summary, InfoRequest

# -----------------------
# "LLM" Stub (offline)
# Swap this with real LLM later
# -----------------------

def fake_llm_classify(email: Email) -> Classification:
    text = (email.subject + " " + email.body).lower()

    # simple keyword heuristics (pretend it's LLM)
    if any(k in text for k in ["invoice", "payment", "billing", "receipt", "refund"]):
        return Classification(route="Billing", urgency="Medium", confidence=0.78, reason="Billing keywords found")
    if any(k in text for k in ["breach", "phishing", "malware", "password", "security"]):
        return Classification(route="Security", urgency="High", confidence=0.88, reason="Security keywords found")
    if any(k in text for k in ["cannot login", "bug", "issue", "error", "support", "help"]):
        return Classification(route="Support", urgency="High" if "urgent" in text else "Medium", confidence=0.80, reason="Support keywords found")
    if any(k in text for k in ["price", "quotation", "quote", "proposal", "demo", "purchase"]):
        return Classification(route="Sales", urgency="Medium", confidence=0.76, reason="Sales keywords found")
    if any(k in text for k in ["resume", "candidate", "interview", "hiring"]):
        return Classification(route="HR", urgency="Low", confidence=0.72, reason="HR keywords found")

    return Classification(route="Unknown", urgency="Low", confidence=0.45, reason="No strong signal")


def fake_llm_summarize(email: Email) -> Summary:
    body = email.body.strip().replace("\n", " ")
    short = body[:160] + ("..." if len(body) > 160 else "")
    bullets = []

    # naive bullet extraction
    for marker in ["-", "*", "•"]:
        if marker in email.body:
            lines = [ln.strip() for ln in email.body.splitlines() if ln.strip().startswith(marker)]
            bullets = [ln.lstrip(marker).strip() for ln in lines[:5]]
            break

    if not bullets:
        bullets = [short]

    return Summary(
        bullets=bullets,
        one_liner=f"{email.subject}: {short}"
    )


def tool_classify(email_text: str) -> str:
    """
    Required by you: tool_classify(email_text)->str
    Returns route label only (string).
    """
    email = Email(subject="(no subject)", sender="unknown", body=email_text)
    return fake_llm_classify(email).route


def tool_summarize(email_text: str) -> str:
    """
    Required by you: tool_summarize(email_text)->str
    Returns a compact 1-liner.
    """
    email = Email(subject="(no subject)", sender="unknown", body=email_text)
    return fake_llm_summarize(email).one_liner


def tool_request_more_info() -> str:
    """
    Required by you: tool_request_more_info()->str
    Returns a fixed template question (stub).
    """
    return "Could you share the missing details (account ID / order number / screenshots) so we can proceed?"


# -----------------------
# Extra tools (more agent-like)
# -----------------------

def tool_extract_entities(email: Email) -> Dict[str, str]:
    """Tiny extractor (replace with LLM / regex / NLP later)."""
    text = (email.subject + "\n" + email.body)
    out = {}

    for key in ["order", "invoice", "ticket", "account"]:
        idx = text.lower().find(key)
        if idx != -1:
            # grab a small window after keyword
            out[key] = text[idx: idx + 50].replace("\n", " ").strip()

    return out


def tool_generate_questions(classification: Classification, entities: Dict[str, str]) -> InfoRequest:
    """
    If unknown route OR low confidence OR missing key entities -> ask questions.
    """
    questions: List[str] = []

    if classification.route == "Billing":
        if not any(k in entities for k in ["invoice", "order", "account"]):
            questions.append("Please provide invoice number or order ID.")
    if classification.route == "Support":
        if "ticket" not in entities:
            questions.append("Do you have an existing ticket ID? If not, what steps reproduce the issue?")
    if classification.route == "Security":
        questions.append("Did you click any link or share credentials? Please forward suspicious headers if possible.")
    if classification.route == "Unknown" or classification.confidence < 0.6:
        questions.append("What outcome do you want from our team (quote/support/billing/security)?")

    return InfoRequest(need_more_info=len(questions) > 0, questions=questions)
