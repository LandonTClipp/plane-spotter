from abc import ABC, abstractmethod
import datetime
import structlog
from textwrap import dedent

from plane_spotter.geolocator import AirportDiscovery


def plane_landed_message(
    source: AirportDiscovery, destination: AirportDiscovery, hashtags: list[str] = []
) -> str:
    return dedent(
        f"""\
        Airplane landed at {destination.airport.name}
        
        Source: {source.airport.ident}: {source.airport.name}
        Destination: {destination.airport.ident}: {destination.airport.name}
        Flight Time: {str(destination.discovery_time - source.discovery_time)}
        Source Region: {source.airport.iso_region}
        Dest Region: {destination.airport.iso_region}
        Discovery Time: {source.discovery_time}

        {' '.join(hashtags)}
        """
    )


def plane_stationed_at_message(airport: AirportDiscovery):
    return dedent(
        f"""\
                Airplane is stationed at {airport.airport.name}
                
                Source: {airport.airport.ident}: {airport.airport.name}
                Source Region: {airport.airport.iso_region}
                Discovery Time: {airport.discovery_time}

                #elonjet
                """
    )


class NotificationBackend(ABC):
    @abstractmethod
    def send(self, message: str, log: structlog.stdlib.BoundLogger):
        ...
