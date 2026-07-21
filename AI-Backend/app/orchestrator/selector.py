from app.domain.schemas.orchestrator import AIMode, OrchestratorRequest

class AIModeSelector:
    """Selects the appropriate AI Mode based on the query if not explicitly provided."""
    
    @staticmethod
    def detect_mode(request: OrchestratorRequest) -> AIMode:
        if request.mode:
            return request.mode
            
        if not request.query:
            return AIMode.GENERAL_AI
            
        query_lower = request.query.lower()
        if "calendar" in query_lower or "schedule" in query_lower:
            return AIMode.CALENDAR
        if "plan" in query_lower or "roadmap" in query_lower:
            return AIMode.PLANNER
        if "remind" in query_lower or "alert" in query_lower:
            return AIMode.REMINDER
        if "assignment" in query_lower or "deadline" in query_lower:
            return AIMode.ASSIGNMENT
        if "flashcard" in query_lower:
            return AIMode.FLASHCARDS
        if "quiz" in query_lower or "test" in query_lower:
            return AIMode.QUIZ
        if "summary" in query_lower or "summarize" in query_lower:
            return AIMode.SUMMARY
        if "notes" in query_lower:
            return AIMode.STUDY_NOTES
        if "course" in query_lower or "syllabus" in query_lower:
            return AIMode.COURSE_RAG
            
        return AIMode.GENERAL_AI
