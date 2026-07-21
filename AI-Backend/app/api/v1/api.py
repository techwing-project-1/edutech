from fastapi import APIRouter
from app.api.v1.routes import documents, retriever, rag, general, content, summary, flashcards, quiz, study_notes, agent, assignment_agent, calendar_agent, study_planner, notification, reminder_agent, orchestrator, monitoring, configuration
from app.modules.hod_analytics.router import router as hod_analytics_router

# Import sub-routers for future AI features here
# from app.api.v1.routes import llm_router

api_router = APIRouter()

# Register sub-routers to the main v1 router
api_router.include_router(documents.router, prefix="/documents", tags=["Document Indexing"])
api_router.include_router(retriever.router, prefix="/retriever", tags=["RAG Retriever"])
api_router.include_router(rag.router, prefix="/rag", tags=["RAG Engine"])
api_router.include_router(general.router, prefix="/general", tags=["General AI Chat"])
api_router.include_router(content.router, prefix="/content", tags=["Content Generation"])
api_router.include_router(summary.router, prefix="/summary", tags=["Summary Generator"])
api_router.include_router(flashcards.router, prefix="/flashcards", tags=["Flashcards Generator"])
api_router.include_router(quiz.router, prefix="/quiz", tags=["Quiz Generator"])
api_router.include_router(study_notes.router, prefix="/study-notes", tags=["Study Notes Generator"])
api_router.include_router(agent.router, prefix="/agent", tags=["OpenClaw Agent Orchestration"])
api_router.include_router(assignment_agent.router, prefix="/agents/assignment", tags=["Assignment Intelligence Agent"])
api_router.include_router(calendar_agent.router, prefix="/agents/calendar", tags=["Calendar Intelligence Agent"])
api_router.include_router(study_planner.router, prefix="/agents/study-planner", tags=["Study Planner Agent"])
api_router.include_router(reminder_agent.router, prefix="/agents/reminder", tags=["Reminder Agent"])
api_router.include_router(notification.router, prefix="/notifications", tags=["Notification Engine"])
api_router.include_router(orchestrator.router, prefix="/orchestrator", tags=["AI Orchestrator"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["Monitoring and Observability"])
api_router.include_router(configuration.router, prefix="/config", tags=["Configuration & Feature Management"])
api_router.include_router(hod_analytics_router, prefix="/hod", tags=["HOD Analytics & AI Insights"])

# api_router.include_router(llm_router.router, prefix="/llm", tags=["LLM Services"])
