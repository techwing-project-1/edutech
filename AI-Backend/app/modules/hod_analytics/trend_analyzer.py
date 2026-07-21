from app.modules.hod_analytics.request_models import AnalyticsPayload

class TrendAnalyzer:
    """Analyzes attendance and performance trends over the semester."""
    
    @staticmethod
    def generate_trend_prompt(data: AnalyticsPayload) -> str:
        prompt = "Analyze the following department trends:\n"
        prompt += f"Semester: {data.semester}\n"
        prompt += f"Attendance Percentage: {data.attendance_percentage}%\n"
        prompt += f"Assignment Completion Rate: {data.assignment_completion_rate}%\n"
        prompt += "Faculty Activity:\n"
        for fac in data.faculty_stats:
            prompt += f"- {fac.faculty_name}: {fac.classes_taken} classes, {fac.materials_uploaded} uploads\n"
            
        prompt += "\nIdentify trends in student engagement, attendance, and faculty activity. Provide insights on whether these trends are positive or negative."
        return prompt
