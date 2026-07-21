import asyncio
from typing import Any
from app.domain.schemas.orchestrator import AIMode, OrchestratorRequest
from app.orchestrator.registry import ServiceRegistry
from app.core.exceptions import OrchestratorException, OrchestratorValidationError
from app.core.logger import logger

from app.agents.manager import AgentManager
from app.domain.schemas.agent import AgentRequest, AgentType

class RequestRouter:
    """Routes the orchestrator request to the correct registered internal service."""
    
    @staticmethod
    async def route(mode: AIMode, request: OrchestratorRequest) -> Any:
        handler = ServiceRegistry.get_handler(mode)
        if not handler:
            logger.error(f"No explicit handler registered for {mode}.")
            raise OrchestratorValidationError(f"Unsupported AI Mode: {mode}")
            
        return await handler(request)

# Example Registrations for demonstration of Orchestrator delegating to OpenClaw
async def _handle_calendar(req: OrchestratorRequest):
    agent_manager = AgentManager()
    agent_req = AgentRequest(user_id=req.user_id, agent_type=AgentType.CALENDAR, query=req.query or "", context=req.payload)
    return await agent_manager.orchestrate(agent_req)

async def _handle_assignment(req: OrchestratorRequest):
    agent_manager = AgentManager()
    agent_req = AgentRequest(user_id=req.user_id, agent_type=AgentType.ASSIGNMENT, query=req.query or "", context=req.payload)
    return await agent_manager.orchestrate(agent_req)

async def _handle_study_planner(req: OrchestratorRequest):
    agent_manager = AgentManager()
    agent_req = AgentRequest(user_id=req.user_id, agent_type=AgentType.STUDY_PLANNER, query=req.query or "", context=req.payload)
    return await agent_manager.orchestrate(agent_req)

async def _handle_reminder(req: OrchestratorRequest):
    agent_manager = AgentManager()
    agent_req = AgentRequest(user_id=req.user_id, agent_type=AgentType.REMINDER, query=req.query or "", context=req.payload)
    return await agent_manager.orchestrate(agent_req)

async def _handle_course_rag(req: OrchestratorRequest):
    from app.services.rag.service import RAGService
    from app.domain.schemas.rag import RAGRequest
    service = RAGService()
    rag_req = RAGRequest(
        user_id=req.user_id,
        query=req.query or "",
        document_id=req.payload.get("document_id"),
        department=req.payload.get("department"),
        semester=req.payload.get("semester"),
        subject=req.payload.get("subject"),
        section=req.payload.get("section")
    )
    return await service.execute_query(rag_req)

async def _handle_summary(req: OrchestratorRequest):
    from app.services.summary.service import SummaryService
    from app.domain.schemas.summary import SummaryRequest
    service = SummaryService()
    summary_req = SummaryRequest(
        user_id=req.user_id,
        topic=req.query or "",
        document_id=req.payload.get("document_id"),
        department=req.payload.get("department"),
        semester=req.payload.get("semester"),
        subject=req.payload.get("subject"),
        section=req.payload.get("section")
    )
    return await service.generate_summary(summary_req)

async def _handle_flashcards(req: OrchestratorRequest):
    from app.services.flashcards.service import FlashcardService
    from app.domain.schemas.flashcards import FlashcardRequest
    service = FlashcardService()
    flashcard_req = FlashcardRequest(
        user_id=req.user_id,
        topic=req.query or "",
        document_id=req.payload.get("document_id"),
        department=req.payload.get("department"),
        semester=req.payload.get("semester"),
        subject=req.payload.get("subject"),
        section=req.payload.get("section")
    )
    return await service.generate_flashcards(flashcard_req)

async def _handle_quiz(req: OrchestratorRequest):
    from app.services.quiz.service import QuizService
    from app.domain.schemas.quiz import QuizRequest
    service = QuizService()
    quiz_req = QuizRequest(
        user_id=req.user_id,
        topic=req.query or "",
        document_id=req.payload.get("document_id"),
        department=req.payload.get("department"),
        semester=req.payload.get("semester"),
        subject=req.payload.get("subject"),
        section=req.payload.get("section")
    )
    return await service.generate_quiz(quiz_req)

async def _handle_study_notes(req: OrchestratorRequest):
    from app.services.study_notes.service import StudyNotesService
    from app.domain.schemas.study_notes import StudyNotesRequest
    service = StudyNotesService()
    notes_req = StudyNotesRequest(
        user_id=req.user_id,
        topic=req.query or "",
        document_id=req.payload.get("document_id"),
        department=req.payload.get("department"),
        semester=req.payload.get("semester"),
        subject=req.payload.get("subject"),
        section=req.payload.get("section")
    )
    return await service.generate_notes(notes_req)

ServiceRegistry.register(AIMode.CALENDAR, _handle_calendar)
ServiceRegistry.register(AIMode.ASSIGNMENT, _handle_assignment)
ServiceRegistry.register(AIMode.PLANNER, _handle_study_planner)
ServiceRegistry.register(AIMode.REMINDER, _handle_reminder)
ServiceRegistry.register(AIMode.COURSE_RAG, _handle_course_rag)
ServiceRegistry.register(AIMode.SUMMARY, _handle_summary)
ServiceRegistry.register(AIMode.FLASHCARDS, _handle_flashcards)
ServiceRegistry.register(AIMode.QUIZ, _handle_quiz)
ServiceRegistry.register(AIMode.STUDY_NOTES, _handle_study_notes)

async def _handle_general_ai(req: OrchestratorRequest):
    from app.services.general_ai.manager import GeneralAIManager
    from app.domain.schemas.general_ai import GeneralAIRequest
    manager = GeneralAIManager()
    gen_req = GeneralAIRequest(
        query=req.query or "",
        session_id=req.user_id # Using user_id as session_id for now if none provided
    )
    return await manager.chat(gen_req)

ServiceRegistry.register(AIMode.GENERAL_AI, _handle_general_ai)

async def _handle_hod_analytics(req: OrchestratorRequest):
    from app.modules.hod_analytics.analytics_service import HODAnalyticsService
    from app.modules.hod_analytics.request_models import HODAnalyticsRequest, AnalyticsPayload
    service = HODAnalyticsService()
    hod_req = HODAnalyticsRequest(
        user_id=req.user_id,
        query=req.query,
        data=AnalyticsPayload(**req.payload)
    )
    return await service.analyze(hod_req)

async def _handle_department_report(req: OrchestratorRequest):
    from app.modules.hod_analytics.analytics_service import HODAnalyticsService
    from app.modules.hod_analytics.request_models import HODAnalyticsRequest, AnalyticsPayload
    service = HODAnalyticsService()
    hod_req = HODAnalyticsRequest(
        user_id=req.user_id,
        query=req.query,
        data=AnalyticsPayload(**req.payload)
    )
    return await service.generate_report(hod_req)

async def _handle_risk_analysis(req: OrchestratorRequest):
    from app.modules.hod_analytics.analytics_service import HODAnalyticsService
    from app.modules.hod_analytics.request_models import HODAnalyticsRequest, AnalyticsPayload
    service = HODAnalyticsService()
    hod_req = HODAnalyticsRequest(
        user_id=req.user_id,
        query=req.query,
        data=AnalyticsPayload(**req.payload)
    )
    return await service.generate_recommendations(hod_req)

ServiceRegistry.register(AIMode.HOD_ANALYTICS, _handle_hod_analytics)
ServiceRegistry.register(AIMode.DEPARTMENT_REPORT, _handle_department_report)
ServiceRegistry.register(AIMode.RISK_ANALYSIS, _handle_risk_analysis)

async def _handle_notification(req: OrchestratorRequest):
    from app.services.notification.manager import NotificationManager
    from app.domain.schemas.notification import NotificationRequest
    manager = NotificationManager()
    
    # Try to extract required fields from payload
    title = req.payload.get("title", "New Notification")
    message = req.payload.get("message", req.query or "You have a new notification.")
    category = req.payload.get("category", "SYSTEM")
    
    notif_req = NotificationRequest(
        user_id=req.user_id,
        title=title,
        message=message,
        category=category,
        metadata=req.payload.get("metadata", {})
    )
    return await manager.create(notif_req)

ServiceRegistry.register(AIMode.NOTIFICATION, _handle_notification)
