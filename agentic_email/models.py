from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, Literal, List, Dict


EmailRoute = Literal["Sales", "Support", "Billing", "Security", "HR", "Unknown"]
Urgency = Literal["Low", "Medium", "High"]


class Email(BaseModel):
    subject: str
    sender: str
    body: str


class Classification(BaseModel):
    route: EmailRoute = "Unknown"
    urgency: Urgency = "Low"
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    reason: str = ""


class Summary(BaseModel):
    bullets: List[str] = Field(default_factory=list)
    one_liner: str = ""


class InfoRequest(BaseModel):
    need_more_info: bool = False
    questions: List[str] = Field(default_factory=list)


class ActionLog(BaseModel):
    level: str
    steps: List[str] = Field(default_factory=list)
    outputs: Dict[str, object] = Field(default_factory=dict)
