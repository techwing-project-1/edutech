from abc import ABC, abstractmethod
from app.domain.schemas.notification import DeliveryType
from app.core.logger import logger

class BaseDeliveryStrategy(ABC):
    @abstractmethod
    async def deliver(self, formatted_message: str, target: str) -> bool:
        pass

class InAppDeliveryStrategy(BaseDeliveryStrategy):
    async def deliver(self, formatted_message: str, target: str) -> bool:
        logger.info(f"Delivering IN_APP notification to {target}: {formatted_message}")
        return True

class EmailDeliveryStrategy(BaseDeliveryStrategy):
    async def deliver(self, formatted_message: str, target: str) -> bool:
        logger.info(f"Delivering EMAIL to {target}")
        return True # Mock for future

class NotificationFactory:
    """Factory to get the correct delivery strategy."""
    
    _strategies = {
        DeliveryType.IN_APP: InAppDeliveryStrategy(),
        DeliveryType.EMAIL: EmailDeliveryStrategy(),
    }
    
    @classmethod
    def get_strategy(cls, delivery_type: DeliveryType) -> BaseDeliveryStrategy:
        # Default to IN_APP if not found (e.g. SMS, PUSH are future)
        return cls._strategies.get(delivery_type, InAppDeliveryStrategy())
