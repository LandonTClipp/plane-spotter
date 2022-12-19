from abc import ABC, abstractmethod
import structlog


class NotificationBackend(ABC):
    @abstractmethod
    def send(self, message: str, log: structlog.stdlib.BoundLogger):
        ...
