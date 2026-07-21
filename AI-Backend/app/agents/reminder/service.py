import json
import uuid
from typing import List
from datetime import datetime, timezone
from app.domain.schemas.reminder_agent import (
    ReminderRequest, ReminderResponse, ReminderListResponse, ReminderType, ReminderPayload
)
from app.domain.schemas.study_planner import StudyPlannerRequest, StudyIntensity
from app.domain.schemas.notification import NotificationRequest, NotificationCategory, NotificationPriority
from app.agents.study_planner.manager import StudyPlannerManager
from app.services.notification.manager import NotificationManager
from app.services.llm.manager import LLMManager
from app.services.llm.parser import extract_text
from app.domain.schemas.llm import LLMRequest
from app.agents.reminder.scheduler import reminder_scheduler
from app.core.exceptions import ReminderAgentException
from app.core.logger import logger

class ReminderService:
    def __init__(self):
        self.study_planner_manager = StudyPlannerManager()
        self.notification_manager = NotificationManager()
        self.llm_manager = LLMManager()

    async def create_reminders(self, request: ReminderRequest) -> ReminderListResponse:
        try:
            # 1. Reuse Study Planner Agent (which reuses Calendar & Assignment)
            study_req = StudyPlannerRequest(
                user_id=request.user_id,
                department=request.department,
                semester=request.semester,
                subject=request.subject,
                section=request.section,
                study_hours_per_day=2.0,
                study_intensity=StudyIntensity.NORMAL,
                preferred_study_timings="Evening"
            )
            study_plan = await self.study_planner_manager.generate(study_req)
            
            # 2. Convert Study Plan to Reminders using LLM
            system_prompt = (
                "You are an AI Reminder Scheduler.\n"
                "You will receive a comprehensive study plan (daily, weekly, exams).\n"
                "Generate logical reminders for these events.\n"
                "Return ONLY a valid JSON array of objects with the keys:\n"
                "reminder_type (ASSIGNMENT, EXAM, REVISION, LAB, PROJECT, STUDY_SESSION),\n"
                "reminder_time (ISO 8601),\n"
                "priority (LOW, MEDIUM, HIGH, CRITICAL),\n"
                "title (string),\n"
                "message (string),\n"
                "category (ASSIGNMENT, EXAM, REVISION, STUDY_PLAN, QUIZ).\n"
                "No markdown wrapping."
            )
            
            prompt = (
                f"Study Plan Data:\n{study_plan.model_dump_json()}\n\n"
                "Generate the reminders array."
            )
            
            llm_request = LLMRequest(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.2,
                max_tokens=3000
            )
            
            llm_response = await self.llm_manager.generate_response(llm_request)
            
            # Parse JSON
            raw_text = extract_text(llm_response).strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:-3]
            elif raw_text.startswith("```"):
                raw_text = raw_text[3:-3]
            
            try:
                reminders_data = json.loads(raw_text)
                if not isinstance(reminders_data, list):
                    reminders_data = [reminders_data]
            except json.JSONDecodeError:
                reminders_data = []

            reminders = []
            
            for r_data in reminders_data:
                # Map enums safely
                r_type_str = r_data.get("reminder_type", "STUDY_SESSION")
                if r_type_str not in [e.value for e in ReminderType]:
                    r_type_str = "STUDY_SESSION"
                r_type = ReminderType(r_type_str)
                
                cat_str = r_data.get("category", "STUDY_PLAN")
                if cat_str not in [e.value for e in NotificationCategory]:
                    cat_str = "STUDY_PLAN"
                cat = NotificationCategory(cat_str)
                
                prio_str = r_data.get("priority", "MEDIUM")
                if prio_str not in [e.value for e in NotificationPriority]:
                    prio_str = "MEDIUM"
                prio = NotificationPriority(prio_str)
                
                sched_time = r_data.get("reminder_time", datetime.now(timezone.utc).isoformat())
                title = r_data.get("title", "Reminder")
                message = r_data.get("message", "You have an upcoming task.")
                
                payload = ReminderPayload(
                    title=title,
                    message=message,
                    category=cat,
                    priority=prio,
                    scheduled_for=sched_time
                )
                
                rem_id = str(uuid.uuid4())
                
                reminder = ReminderResponse(
                    reminder_id=rem_id,
                    user_id=request.user_id,
                    reminder_type=r_type,
                    reminder_time=sched_time,
                    priority=prio,
                    notification_payload=payload,
                    status="SCHEDULED"
                )
                
                # 1. Schedule internally
                reminder_scheduler.schedule(reminder)
                reminders.append(reminder)
                
                # 2. Push to Notification Engine
                # Hardcoding string imports for simplicity, or we can use ENUM dynamically
                from app.domain.schemas.notification import DeliveryType
                
                notif_req = NotificationRequest(
                    user_id=request.user_id,
                    title=title,
                    message=message,
                    category=cat,
                    priority=prio,
                    delivery_types=[DeliveryType.IN_APP],
                    scheduled_for=sched_time,
                    metadata={"reminder_id": rem_id}
                )
                
                await self.notification_manager.create(notif_req)
                
            return ReminderListResponse(total=len(reminders), reminders=reminders)

        except Exception as e:
            logger.error(f"Failed to generate reminders: {str(e)}")
            raise ReminderAgentException(f"Generation failed: {str(e)}")

    def get_by_user(self, user_id: str) -> ReminderListResponse:
        rems = reminder_scheduler.get_by_user(user_id)
        return ReminderListResponse(total=len(rems), reminders=rems)
        
    def delete_reminder(self, reminder_id: str) -> bool:
        return reminder_scheduler.delete(reminder_id)
