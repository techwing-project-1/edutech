from pydantic_settings import BaseSettings

class OpenClawConfig(BaseSettings):
    """
    Configuration settings for the OpenClaw Agent Framework.
    """
    AGENT_TIMEOUT_SECONDS: int = 30
    ENABLE_AGENT_MEMORY: bool = True
    MAX_CONCURRENT_AGENTS: int = 10
    
    class Config:
        env_prefix = "OPENCLAW_"

agent_config = OpenClawConfig()
