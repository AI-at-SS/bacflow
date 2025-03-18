import pytest

from bacflow.geolocation import (
    _location_to_ISO_alpha_2,
    get_DUI_threshold,
    get_location,
)
from bacflow.schemas import DriverProfile, DUIMapping


@pytest.fixture
def mapping() -> DUIMapping:
    return {"US": {DriverProfile.regular: 0.05}}


@pytest.mark.asyncio
async def test_get_location():
    assert _location_to_ISO_alpha_2(await get_location(33.749, -84.388)) == "US"


@pytest.mark.asyncio
async def test_get_DUI_threshold(mapping: DUIMapping):
    assert (await get_DUI_threshold(33.749, -84.388, DriverProfile.regular, mapping)) == 0.05


@pytest.mark.asyncio
async def test_get_DUI_threshold_failure_for_ISO_alpha_2(mapping: DUIMapping):
    assert not (await get_DUI_threshold(33.749, -14.006, DriverProfile.regular, mapping))


@pytest.mark.asyncio
async def test_get_DUI_threshold_failure_for_profile(mapping: DUIMapping):
    assert not (await get_DUI_threshold(33.749, -84.388, DriverProfile.professional, mapping))
