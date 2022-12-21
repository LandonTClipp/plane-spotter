import pytest

from plane_spotter.geolocator import Geolocator
from plane_spotter.package import airport_code_path
from testfixtures import compare


@pytest.mark.parametrize(
    ("coordinates", "distance", "expected"),
    [
        (
            (33.92055294963162, -118.32755477360656),
            10,
            "Jack Northrop Field Hawthorne Municipal Airport",
        ),
        (
            (37.39404842978427, -122.14982702193727),
            10,
            "Palo Alto Airport of Santa Clara County",
        ),
        (
            (38.89804315682689, -77.0040050557741),
            10,
            "Ronald Reagan Washington National Airport",
        ),
        ((38.89804315682689, -77.0040050557741), 1, None),
    ],
)
def test_lookup_airport(coordinates, distance, expected):
    geolocator = Geolocator(airport_code_file=airport_code_path())
    airport = geolocator.lookup_airport(coordinates=coordinates, max_distance=distance)

    compare(expected=expected, actual=airport.name if airport is not None else None)
