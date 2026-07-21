import os
from app.services.prompts.registry import PromptRegistry
from app.domain.schemas.prompt import PromptTemplateSchema, PromptMetadata
from app.services.prompts.constants import PromptCategory, PromptType

# Get the absolute path to the templates directory to ensure robustness regardless of execution context
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_TEMPLATES_DIR = os.path.join(_BASE_DIR, "templates")

# ==========================================
# Bootstrap Core Prompt Templates
# ==========================================

# 1. General AI - System
PromptRegistry.register(
    PromptTemplateSchema(
        name="general_ai_system_v1",
        prompt_type=PromptType.SYSTEM,
        metadata=PromptMetadata(
            category=PromptCategory.GENERAL_AI,
            description="Default system instructions for the General AI Chat.",
            tags=["core", "system", "tutor"]
        ),
        template_path=os.path.join(_TEMPLATES_DIR, "system", "general_ai_system.txt"),
        variables=[]
    )
)

# 2. General AI - User
PromptRegistry.register(
    PromptTemplateSchema(
        name="general_ai_user_v1",
        prompt_type=PromptType.USER,
        metadata=PromptMetadata(
            category=PromptCategory.GENERAL_AI,
            description="Default user template for General AI Chat processing.",
            tags=["core", "user"]
        ),
        template_path=os.path.join(_TEMPLATES_DIR, "user", "general_ai_user.txt"),
        variables=["user_query", "history"]
    )
)

# 3. Course Assistant - System
PromptRegistry.register(
    PromptTemplateSchema(
        name="course_assistant_system_v1",
        prompt_type=PromptType.SYSTEM,
        metadata=PromptMetadata(
            category=PromptCategory.COURSE_ASSISTANT,
            description="System instructions for answering academic course questions.",
            tags=["core", "system", "course"]
        ),
        template_path=os.path.join(_TEMPLATES_DIR, "system", "course_assistant.txt"),
        variables=["context"]
    )
)

# 4. Course Assistant - User
PromptRegistry.register(
    PromptTemplateSchema(
        name="course_assistant_user_v1",
        prompt_type=PromptType.USER,
        metadata=PromptMetadata(
            category=PromptCategory.COURSE_ASSISTANT,
            description="User prompt for answering academic course questions.",
            tags=["core", "user", "course"]
        ),
        template_path=os.path.join(_TEMPLATES_DIR, "user", "course_assistant.txt"),
        variables=["question"]
    )
)
