import requests
from typing import Optional


class ADSBExchange:
    def __init__(self, key: str, hostname: str = "adsbexchange-com1.p.rapidapi.com"):
        self._hostname = hostname
        self._key = key
        self._base_url = f"https://{self._hostname}/v2/"

    def _headers(self) -> dict:
        return {
            "X-RapidAPI-Key": self._key,
            "X-RapidAPI-Host": self._hostname,
        }

    def _url(self, path: list[str]) -> str:
        return self._base_url + "/".join(path) + "/"

    def GET(self, path: list[str], headers: Optional[dict] = None) -> requests.Response:
        if headers is None:
            headers = dict()

        return requests.request(
            "GET", self._url(path=path), headers={**self._headers(), **headers}
        )

    def position_by_registration(self, registration: str) -> requests.Response:
        return self.GET(path=["registration", registration])

    def aircraft_by_callsign(self, callsign: str) -> requests.Response:
        return self.GET(path=["callsign", callsign])

    def aircraft_last_position_by_hex_id(self, hex_id: str) -> requests.Response:
        return self.GET(path=["hex", hex_id])
