from app.domain.schemas.configuration import SystemConfiguration, FeatureFlag
from app.configuration.environment import EnvironmentManager
from app.configuration.features import FeatureFlagManager
from app.configuration.provider_config import ProviderConfig, VectorDBConfig, AgentConfig, ModelConfig

class ConfigurationManager:
    """Facade for gathering all configurations system-wide."""
    
    @staticmethod
    def get_system_configuration() -> SystemConfiguration:
        return SystemConfiguration(
            environment=EnvironmentManager.get_profile(),
            providers=ProviderConfig.load(),
            vector_db=VectorDBConfig.load(),
            agents=AgentConfig.load(),
            models=ModelConfig.load()
        )
        
    @staticmethod
    def reload_configuration() -> None:
        """
        In a real distributed system, this would pull fresh configs from 
        AWS Parameter Store, Consul, or a DB without restarting the app.
        For now, it simulates a refresh.
        """
        pass
        
    @staticmethod
    def get_features() -> dict:
        return FeatureFlagManager.get_all()
        
    @staticmethod
    def update_feature(feature: FeatureFlag, enabled: bool) -> None:
        FeatureFlagManager.set_feature(feature, enabled)
