import geopy
from geopy.adapters import AioHTTPAdapter
from geopy.geocoders import Nominatim

from bacflow.logging import get_logger
from bacflow.schemas import DriverProfile, DUIMapping


logging = get_logger()


class MissingDUI4ISOException(Exception):
    """raises when a ISO alpha-2 country code is not found in the DUI mapping"""

    def __init__(self, ISO_alpha_2: str):
        self.message = f"No DUI threshold for country {ISO_alpha_2}"
        super().__init__(self.message)


class MissingDUI4DriverProfileInISOException(Exception):
    """raises when a driver profile is not found for a ISO alpha-2 country code in the DUI mapping"""

    def __init__(self, ISO_alpha_2: str, profile: DriverProfile):
        self.message = f"No DUI threshold for {profile} drivers in {ISO_alpha_2}"
        super().__init__(self.message)


def _location_to_ISO_alpha_2(location: geopy.Location) -> str:
    """ISO alpha-2 country code of a location"""
    return location.raw["address"]["country_code"].upper()


def _ISO_alpha_2_to_DUI_threshold(
    ISO_alpha_2: str, profile: DriverProfile, mapping: DUIMapping
) -> float:
    """driving under the influence (DUI) threshold by ISO alpha-2 country code and driver profile"""
    if not mapping.get(ISO_alpha_2):
        raise MissingDUI4ISOException(ISO_alpha_2)

    if not mapping[ISO_alpha_2].get(profile):
        raise MissingDUI4DriverProfileInISOException(ISO_alpha_2, profile)

    return mapping[ISO_alpha_2][profile]


async def get_location(latitude: float, longitude: float) -> geopy.Location:
    """reverse geocoding by latitude and longitude"""
    async with Nominatim(user_agent="BACflow", adapter_factory=AioHTTPAdapter) as geolocator:
        return await geolocator.reverse((latitude, longitude), exactly_one=True)


async def get_DUI_threshold(
    latitude: float,
    longitude: float,
    profile: DriverProfile,
    mapping: DUIMapping,
) -> float:
    """driving under the influence (DUI) threshold by coordinates and driver profile"""
    ISO_alpha_2 = _location_to_ISO_alpha_2(await get_location(latitude, longitude))
    threshold = _ISO_alpha_2_to_DUI_threshold(ISO_alpha_2, profile, mapping)

    return threshold
