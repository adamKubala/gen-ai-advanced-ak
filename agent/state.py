from typing import Literal, NotRequired, TypedDict, Any
from pydantic import BaseModel

Intent = Literal[
    "northwind_query",
    "document_search",
    "reporting",
    "out_of_scope",
    "security_breach",
]

class IntentResult(BaseModel):
    intent: Intent
    reason: str

class AgentState(TypedDict):
    question: str
    intent: NotRequired[IntentResult]

StateUpdate = dict[str, Any]