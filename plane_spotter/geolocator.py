from typing import Any

import csv
import haversine

AIRPORT_TYPE_BLACKLIST = set(('balloonport', 'closed', 'heliport', 'seaplane_base'))

class Geolocator:
  ''' Translates coordinates to the closest airport. '''

  def __init__(self, airport_code_file: str='plane_spotter/data/airport-codes.csv') -> 'Geolocator':
    ''' Initializes a Geolocator object '''
    self.__airports = []
    # Add airport dict for each row in airport_code_file
    with open(airport_code_file, 'r') as file:
      for airport in csv.DictReader(file):
        # Add it if it's not a blacklisted type
        if airport['type'] not in AIRPORT_TYPE_BLACKLIST:
          coordinates = airport['coordinates'].split(', ')
          airport['coordinates'] = (float(coordinates[0]), float(coordinates[1]))
          self.__airports.append(airport)
    if len(self.__airports) == 0:
      raise Exception('No airports loaded.')

  def lookup_airport(self, coordinates: tuple[float, float], max_distance: float) -> dict[str, Any] | None:
    ''' Finds the closest airport to any set of coordinates that is within
    max_distance (in miles) and returns that airport as a dict of each element
    in the airport_code_file passed in during initialization.
    If no airport is found, returns None. '''
    closest = None
    closest_distance = max_distance
    for airport in self.__airports:
      distance = self.__distance(coordinates, airport['coordinates'])
      if distance <= closest_distance:
        closest = airport
        closest_distance = distance
    return closest


  def __distance(self, a: tuple[float, float], b: tuple[float, float]) -> float:
    ''' Calculates the distance between 2 coordinates '''
    return haversine.haversine(a, b, unit=haversine.Unit.MILES)


if __name__ == '__main__':
  geolocator = Geolocator()

  tests = [
    {
      'coordinates': (33.92055294963162, -118.32755477360656),
      'dist': 10,
      'expected': 'Jack Northrop Field Hawthorne Municipal Airport'
    },
    {
      'coordinates': (37.39404842978427, -122.14982702193727),
      'dist': 10,
      'expected': 'Palo Alto Airport of Santa Clara County'
    },
    {
      'coordinates': (38.89804315682689, -77.0040050557741),
      'dist': 10,
      'expected': 'Ronald Reagan Washington National Airport'
    },
    {
      'coordinates': (38.89804315682689, -77.0040050557741),
      'dist': 1,
      'expected': None
    }
  ]

  # Yes, I know there's testing frameworks. I just wanted something simple.
  for test in tests:
    airport = geolocator.lookup_airport(test['coordinates'], test['dist'])
    if airport is not None:
      airport = airport['name']

    print(f'Lookup for airports within {test["dist"]} mile of ' \
          f'{test["coordinates"]} returned {airport}.')

    if airport != test['expected']:
      raise Exception(f'Expected {test["expected"]}.')
