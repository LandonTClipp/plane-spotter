from typing import Any

class Geolocator:
  ''' Translates coordinates to the closest airport. '''

  def __init__(self, airport_code_file: str='plane_spotter/data/airport-codes.csv') -> 'Geolocator':
    ''' Initializes a Geolocator object '''
    pass

  def lookup_airport(self, coordinates: tuple[float, float], max_distance: float) -> dict[str, Any] | None:
    ''' Finds the closest airport to any set of coordinates that is within
    max_distance (in miles) and returns that airport as a dict of each element
    in the airport_code_file passed in during initialization.
    If no airport is found, returns None. '''
    pass
