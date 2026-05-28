from models.email_models import RawEmail, PipelineOutput, ClassificationResult
from preprocessing.parser import preprocess_email
from classification.safety_classifier import SafetyClassifier
from classification.source_classifier import SourceClassifier
from classification.intent_classifier import IntentClassifier
from classification.priority_classifier import PriorityClassifier
from classification.llm_classifier import LLMIntentSourceClassifier
from decision_engine.workflow_router import route_workflow
from context.context_builder import build_llm_context
from utils.logger import logger
from config.settings import settings

if settings.LLM_PROVIDER.lower() == "gemini":
    from llm.gemini_provider import GeminiProvider as ActiveLLMProvider
else:
    from llm.openai_provider import OpenAIProvider as ActiveLLMProvider

def email_pipeline(raw_email_dict: dict) -> dict:
    raw_email = RawEmail(**raw_email_dict)
    cleaned_email = preprocess_email(raw_email)
    safety_label = SafetyClassifier().classify(cleaned_email)
    source_label = SourceClassifier().classify(cleaned_email)
    intent_label = IntentClassifier().classify(cleaned_email)
    priority_label = PriorityClassifier().classify(cleaned_email)
    # LLM-based classification enrichment for ambiguous/newsletter/suspicious
    llm_aug = None
    if (
        source_label in ("broadcast_newsletter", "unknown") or
        intent_label in ("informational", "unknown") or
        safety_label in ("suspicious",)
    ):
        llm_classifier = LLMIntentSourceClassifier()
        llm_aug = llm_classifier.classify(cleaned_email)
        if llm_aug.get("source") and llm_aug.get("intent"):
            source_label = llm_aug["source"]
            intent_label = llm_aug["intent"]
    classification = ClassificationResult(
        safety=safety_label,
        source=source_label,
        intent=intent_label,
        priority=priority_label
    )
    action = route_workflow(classification)
    llm_context = build_llm_context(cleaned_email, classification, action)
    draft, summary, reasoning = None, None, None
    if action.action in ["generate_draft", "generate_draft_and_notify"]:
        provider = ActiveLLMProvider()
        llm_out = provider.generate(llm_context)
        draft = llm_out.get("draft")
        summary = llm_out.get("summary", "")
        reasoning = llm_out.get("reasoning", "")
    elif action.action == "summarize_only":
        provider = ActiveLLMProvider()
        llm_out = provider.generate(llm_context)
        draft = ""
        summary = llm_out.get("draft")
        reasoning = llm_out.get("reasoning", "")
    else:
        draft, summary, reasoning = "", "", action.reasoning
    output = PipelineOutput(
        classification=classification,
        action=action.action,
        draft=draft,
        summary=summary,
        reasoning=reasoning,
        requires_human_review=action.requires_human_review
    )
    # Optionally, expose the raw LLM classification in output for transparency
    result = output.dict()
    if llm_aug:
        result["llm_classification"] = llm_aug
    logger.info(f"Pipeline output: {result}")
    return result
