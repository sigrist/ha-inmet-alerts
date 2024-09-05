"""Example integration using DataUpdateCoordinator."""

from datetime import timedelta
import logging

import aiohttp
import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import GEOCODE

_LOGGER = logging.getLogger(__name__)


class InMetAlertsCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass: HomeAssistant, data) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="InMet",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=30),
        )
        self.settings = data

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """

        # Note: asyncio.TimeoutError and aiohttp.ClientError are already
        # handled by the data update coordinator.
        async with async_timeout.timeout(10):
            # Grab active context variables to limit data required to be fetched from API
            # Note: using context is not required if there is no need or ability to limit
            # data retrieved from API.
            settings = self.settings
            geocode = settings[GEOCODE]
            _LOGGER.debug(f"Settings: {settings}")  # noqa: G004

            api_response = await self.async_call_api()

            response = {}
            response["state"] = 0
            response["alerts"] = []

            today = api_response["hoje"]
            for alert in today:
                geocodes = alert["geocodes"].split(",")

                if geocode in geocodes:
                    response["alerts"].append(alert)
                    response["state"] = "on"

            futuro = api_response["futuro"]
            for alert in futuro:
                geocodes = alert["geocodes"].split(",")

                if geocode in geocodes:
                    alert["future"] = True
                    response["alerts"].append(alert)
                    response["state"] = "on"

            response["state"] = len(response["alerts"])
            return response

    async def async_call_api(self) -> dict:
        response = None
        url = "https://apiprevmet3.inmet.gov.br/avisos/ativos"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as r:
                    _LOGGER.debug("Response: %s", r.status)

                    if r.status == 200:
                        response = await r.json()
            except:
                response = None

        return response
