import geopy
from geopy.adapters import AioHTTPAdapter
from geopy.geocoders import Nominatim

from bacflow.logging import get_logger
from bacflow.schemas import DriverProfile, DUIMapping


logging = get_logger()


def _location_to_ISO_alpha_2(location: geopy.Location) -> str:
    """ISO alpha-2 country code of a location"""
    return location.raw["address"]["country_code"].upper()


async def get_location(latitude: float, longitude: float) -> geopy.Location:
    """reverse geocoding by latitude and longitude"""
    async with Nominatim(user_agent="BACflow", adapter_factory=AioHTTPAdapter) as geolocator:
        return await geolocator.reverse((latitude, longitude), exactly_one=True)


async def get_DUI_threshold(
    latitude: float, longitude: float, profile: DriverProfile, mapping: DUIMapping
) -> float | None:
    """driving under the influence (DUI) threshold by coordinates and driver profile"""
    try:
        location = await get_location(latitude, longitude)
        ISO_alpha_2 = _location_to_ISO_alpha_2(location)

        return mapping[ISO_alpha_2][profile]
    except Exception:
        message = "No DUI threshold for {} drivers at ({:.3f}, {:.3f})"
        message = message.format(profile, latitude, longitude)

        logging.warning(message)

        return  # noqa
