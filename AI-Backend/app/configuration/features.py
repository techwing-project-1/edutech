from typing import Dict
from app.domain.schemas.configuration import FeatureFlag
from app.core.logger import logger

class FeatureFlagManager:
    """In-memory manager for enabling/disabling runtime feature toggles."""
    
    _flags: Dict[FeatureFlag, bool] = {
        FeatureFlag.COURSE_RAG: True,
        FeatureFlag.GENERAL_AI: True,
        FeatureFlag.SUMMARY: True,
        FeatureFlag.FLASHCARDS: True,
        FeatureFlag.QUIZ: True,
        FeatureFlag.STUDY_NOTES: True,
        FeatureFlag.ASSIGNMENT_AGENT: True,
        FeatureFlag.CALENDAR_AGENT: True,
        FeatureFlag.STUDY_PLANNER: True,
        FeatureFlag.REMINDER_AGENT: True,
        FeatureFlag.MONITORING: True,
        FeatureFlag.OPENCLAW: True,
    }
    
    @classmethod
    def get_all(cls) -> Dict[FeatureFlag, bool]:
        return cls._flags.copy()
        
    @classmethod
    def is_enabled(cls, feature: FeatureFlag) -> bool:
        return cls._flags.get(feature, False)
        
    @classmethod
    def set_feature(cls, feature: FeatureFlag, enabled: bool) -> None:
        if feature in cls._flags:
            cls._flags[feature] = enabled
            logger.info(f"Feature flag {feature} set to {enabled}")
        else:
            logger.warning(f"Unknown feature flag: {feature}")
