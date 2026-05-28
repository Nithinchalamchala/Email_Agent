from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class RawEmail(BaseModel):
    sender: str
    subject: str
    body: str
    timestamp: str
    thread_id: str
    metadata: Dict[str, Any]

class CleanedEmail(BaseModel):
    sender: str
    subject: str
    cleaned_body: str
    timestamp: str
    thread_id: str
    metadata: Dict[str, Any]

class ClassificationResult(BaseModel):
    safety: str
    source: str
    intent: str
    priority: str

class WorkflowAction(BaseModel):
    action: str
    requires_human_review: bool
    reasoning: str

class LLMContext(BaseModel):
    sender: str
    cleaned_body: str
    subject: str
    classification: ClassificationResult
    action: WorkflowAction
    tone_guidance: str
    reply_objective: str

class PipelineOutput(BaseModel):
    classification: ClassificationResult
    action: str
    draft: Optional[str]
    summary: Optional[str]
    reasoning: Optional[str]
    requires_human_review: bool
