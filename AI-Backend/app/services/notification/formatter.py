from app.domain.schemas.notification import NotificationRequest
from app.services.notification.templates import NotificationTemplates

class NotificationFormatter:
    """Formats notifications before delivery."""
    
    @staticmethod
    def format(request: NotificationRequest) -> str:
        template = NotificationTemplates.get_template(request.category)
        return template.format(
            title=request.title,
            message=request.message
        )
