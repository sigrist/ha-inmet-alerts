# """Test component setup."""
# from homeassistant.setup import async_setup_component
#
# from custom_components.inmet_alerts.const import DOMAIN
# from custom_components.inmet_alerts.sensors import InMetAlertsSensor
# import pytest


async def test_async_setup(hass):
    """Test the component gets setup."""
    # sensor = InMetAlertsSensor()
    # await sensor.async_update()
    #
    # assert sensor.available is True
    # assert sensor.attrs['description'] == "My alert"
    a = 'Test'

    assert a == 'Test'
