from app.modules.hod_analytics.request_models import HODAnalyticsRequest
from app.modules.hod_analytics.exceptions import HODValidationException

class HODValidator:
    """Validates structural and logical integrity of incoming analytics data."""
    
    @staticmethod
    def validate_request(request: HODAnalyticsRequest):
        if not request.data:
            raise HODValidationException("Analytics data payload is missing.")
            
        data = request.data
        if data.student_count < 0:
            raise HODValidationException("Student count cannot be negative.")
            
        if not (0 <= data.attendance_percentage <= 100):
            raise HODValidationException("Attendance percentage must be between 0 and 100.")
            
        if data.at_risk_students_count > data.student_count:
            raise HODValidationException("At-risk students count cannot exceed total student count.")
            
        return True
