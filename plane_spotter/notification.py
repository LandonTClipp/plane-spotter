from abc import ABC, abstractmethod

class NotificationBackend(ABC):
    @abstractmethod
    def send(self, message: str): ...

class TwitterClient(NotificationBackend):
    def __init__(self):
        pass

    def send(self, message: str):
        pass