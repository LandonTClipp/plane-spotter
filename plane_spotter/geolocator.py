from typing import Any

import csv
import haversine
import pathlib

AIRPORT_TYPE_BLACKLIST = set(("balloonport", "closed", "heliport", "seaplane_base"))
DEFAULT_PATH = pathlib.Path("plane_spotter/data/airport-codes.csv")


class Geolocator:
    """Translates coordinates to the closest airport."""

    def __init__(self, airport_code_file: pathlib.Path = DEFAULT_PATH) -> "Geolocator":
        """Initializes a Geolocator object"""
        self.__airports = []
        # Add airport dict for each row in airport_code_file
        with open(airport_code_file, "r") as file:
            for airport in csv.DictReader(file):
                # Add it if it's not a blacklisted type
                if airport["type"] not in AIRPORT_TYPE_BLACKLIST:
                    coordinates = airport["coordinates"].split(", ")
                    airport["coordinates"] = (
                        float(coordinates[0]),
                        float(coordinates[1]),
                    )
                    self.__airports.append(airport)
        if len(self.__airports) == 0:
            raise ValueError("No airports loaded.")

    def lookup_airport(
        self, coordinates: tuple[float, float], max_distance: float
    ) -> dict[str, Any] | None:
        """Finds the closest airport to any set of coordinates that is within
        max_distance (in kilometers) and returns that airport as a dict of each element
        in the airport_code_file passed in during initialization.
        If no airport is found, returns None."""
        closest = None
        closest_distance = max_distance
        for airport in self.__airports:
            distance = self.__distance(coordinates, airport["coordinates"])
            if distance <= closest_distance:
                closest = airport
                closest["distance_to_coordinates"] = distance
                closest_distance = distance
        return closest

    def __distance(self, a: tuple[float, float], b: tuple[float, float]) -> float:
        """Calculates the distance between 2 coordinates in Kilometers"""
        return haversine.haversine(a, b, unit=haversine.Unit.KILOMETERS)
