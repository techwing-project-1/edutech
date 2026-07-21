from app.domain.schemas.notification import NotificationCategory

class NotificationTemplates:
    """Provides templates for different notification categories."""
    
    TEMPLATES = {
        NotificationCategory.ASSIGNMENT: "Assignment Alert: {title}\nDetails: {message}",
        NotificationCategory.EXAM: "Exam Reminder: {title}\nPrepare well: {message}",
        NotificationCategory.REVISION: "Time for Revision: {title}\n{message}",
        NotificationCategory.STUDY_PLAN: "Your Study Plan Update: {title}\n{message}",
        NotificationCategory.QUIZ: "Quiz Available: {title}\n{message}",
        NotificationCategory.SYSTEM: "System Notice: {title}\n{message}",
    }
    
    @classmethod
    def get_template(cls, category: NotificationCategory) -> str:
        return cls.TEMPLATES.get(category, "{title}\n{message}")
