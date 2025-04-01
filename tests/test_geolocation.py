import geopy
import pytest

from bacflow.geolocation import (
    MissingDUI4DriverProfileInISOException,
    MissingDUI4ISOException,
    _ISO_alpha_2_to_DUI_threshold,
    _location_to_ISO_alpha_2,
)
from bacflow.schemas import DriverProfile, DUIMapping


@pytest.fixture
def ISO_alpha_2_US() -> str:
    return "US"


@pytest.fixture
def ISO_alpha_2_UK() -> str:
    return "UK"


@pytest.fixture
def get_location_US() -> geopy.Location:
    return geopy.Location("", (0.0, 0.0), {"address": {"country_code": "us"}})


@pytest.fixture
def mapping() -> DUIMapping:
    return {"US": {DriverProfile.regular: 0.05}}


def test_location_to_ISO_alpha_2(get_location_US: geopy.Location):
    assert _location_to_ISO_alpha_2(get_location_US) == "US"


def test_ISO_alpha_2_to_DUI_threshold(ISO_alpha_2_US: geopy.Location, mapping: DUIMapping):
    assert _ISO_alpha_2_to_DUI_threshold(ISO_alpha_2_US, DriverProfile.regular, mapping) == 0.05


def test_ISO_alpha_2_to_DUI_threshold_failure_for_ISO_alpha_2(
    ISO_alpha_2_UK: geopy.Location, mapping: DUIMapping
):
    with pytest.raises(MissingDUI4ISOException):
        _ISO_alpha_2_to_DUI_threshold(ISO_alpha_2_UK, DriverProfile.regular, mapping)


def test_ISO_alpha_2_to_DUI_threshold_failure_for_profile(
    ISO_alpha_2_US: geopy.Location, mapping: DUIMapping
):
    with pytest.raises(MissingDUI4DriverProfileInISOException):
        _ISO_alpha_2_to_DUI_threshold(ISO_alpha_2_US, DriverProfile.professional, mapping)
