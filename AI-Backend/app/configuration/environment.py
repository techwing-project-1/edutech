import os
from app.domain.schemas.configuration import EnvironmentProfile

class EnvironmentManager:
    """Manages the application's environment profiles."""
    
    @staticmethod
    def get_profile() -> EnvironmentProfile:
        env_str = os.getenv("APP_ENV", "DEVELOPMENT").upper()
        if env_str in [e.value for e in EnvironmentProfile]:
            return EnvironmentProfile(env_str)
        return EnvironmentProfile.DEVELOPMENT
