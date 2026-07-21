from enum import Enum

class PromptCategory(str, Enum):
    COURSE_ASSISTANT = "course_assistant"
    GENERAL_AI = "general_ai"
    SUMMARY = "summary"
    FLASHCARDS = "flashcards"
    QUIZ = "quiz"
    STUDY_NOTES = "study_notes"
    STUDY_PLANNER = "study_planner"
    FUTURE_CATEGORIES = "future_categories"

class PromptType(str, Enum):
    SYSTEM = "system"
    USER = "user"
