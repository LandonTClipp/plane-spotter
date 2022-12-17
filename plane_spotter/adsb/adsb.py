from abc import ABC, abstractmethod


class ADSB(ABC):
    """
    Abstract class for implementing a common interface to
    some ADS-B backend.
    """

    @abstractmethod
    def GET(self): ...

    
