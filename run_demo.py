from agentic_email.models import Email
from agentic_email.level1_rpa_with_ai import handle_email_level1
from agentic_email.level2_orchestrated_workflow_agent import handle_email_level2
from agentic_email.level3_react_agent import handle_email_level3
from agentic_email.level4_planning_multi_step_agent import handle_email_level4


SAMPLES = [
    Email(
        subject="Urgent: Payment failed for invoice #A-11902",
        sender="customer@acme.com",
        body="Hi team,\nOur payment failed but we got charged. Please help.\nInvoice: A-11902\nThanks",
    ),
    Email(
        subject="Security Incident",
        sender="it-admin@client.gov",
        body="We suspect phishing emails reached multiple employees. Need immediate assistance.\nPlease advise response steps.",
    ),
    Email(
        subject="Need a quotation for automation project",
        sender="procurement@bigco.com",
        body="Hello,\nWe want a proposal and pricing for RPA + GenAI workflow for invoice processing.\nTimeline: Q2.\nRegards",
    ),
    Email(
        subject="???",
        sender="mystery@unknown.com",
        body="Can you do it? Need help asap.",
    ),
]

def pretty(title: str, obj):
    print("\n" + "="*80)
    print(title)
    print("="*80)
    print("STEPS:")
    for s in obj.steps:
        print("-", s)
    print("\nOUTPUTS:")
    for k, v in obj.outputs.items():
        print(f"- {k}: {v}")


def main():
    for idx, email in enumerate(SAMPLES, start=1):
        print("\n" + "#"*80)
        print(f"EMAIL SAMPLE #{idx} | subject={email.subject!r} | sender={email.sender}")
        print("#"*80)

        pretty("LEVEL 1", handle_email_level1(email))
        pretty("LEVEL 2", handle_email_level2(email))
        pretty("LEVEL 3", handle_email_level3(email))
        pretty("LEVEL 4", handle_email_level4(email))


if __name__ == "__main__":
    main()
