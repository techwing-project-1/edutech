from app.modules.hod_analytics.request_models import AnalyticsPayload

class RiskAnalyzer:
    """Analyzes student metrics to identify academic risks and weak subjects."""
    
    @staticmethod
    def generate_risk_prompt(data: AnalyticsPayload) -> str:
        prompt = "Analyze the following data to identify academic risks:\n"
        prompt += f"At Risk Students: {data.at_risk_students_count} out of {data.student_count}\n"
        prompt += f"Average Marks: {data.average_marks}%\n"
        prompt += f"Course Completion: {data.course_completion_percentage}%\n"
        prompt += "Subject Performance:\n"
        for subj in data.subject_performance:
            prompt += f"- {subj.subject_name}: {subj.average_marks}% average, {subj.pass_percentage}% pass rate\n"
        
        prompt += "\nIdentify specific weak subjects, courses with low completion, and the severity of the at-risk student population."
        return prompt
