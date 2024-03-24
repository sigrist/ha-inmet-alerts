from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import Entity

import logging
from typing import Any, Callable, Optional

from homeassistant.helpers.typing import (HomeAssistantType, DiscoveryInfoType, ConfigType)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from inmet import inmet

from .const import (ATTR_DESCRIPTION, ATTR_DESCRIPTION_INMET, INMET_URL)

_LOGGER = logging.getLogger(__name__)
# Time between updating data from InMet
SCAN_INTERVAL = timedelta(minutes=10)

# async def async_setup(hass: HomeAssistant, config: dict):
#     """Configuração do componente no nível da plataforma."""
#     # O seu componente pode necessitar de configuração adicional aqui
#     return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    # """Configuração de uma entrada específica (config flow)."""
    # hass.data.setdefault(DOMAIN, {})
    #
    # # Aqui, você inicializa seu sensor ou outra lógica específica
    # # Por exemplo, carregar uma instância do seu sensor
    # hass.async_create_task(
    #     hass.config_entries.async_forward_entry_setup(entry, "sensor")
    # )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Tratamento para descarregar uma entrada do componente."""
    # Aqui, você pode adicionar lógica para descarregar recursos
    # Se você definiu um sensor, por exemplo, é aqui que você deve removê-lo
    # await hass.config_entries.async_forward_entry_unload(entry, "sensor")

    return True


async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the sensor platform."""

    sensors = [InMetAlertsSensor(INMET_URL)]
    async_add_entities(sensors, update_before_add=True)

class InMetAlertsSensor(Entity):
    """Representation of a GitHub Repo sensor."""

    def __init__(self, inmet_url):
        super().__init__()
        self.attrs: dict[str, Any] = {}
        self._name = "InMet Alerts"
        self._state = 'off'
        self._available = True
        self._inmet_url = inmet_url

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        # todo Unique id?
        return '12345'

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def state(self) -> str | None:
        return self._state

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return self.attrs

    async def async_update(self) -> None:
        """Update all sensors."""
        try:
            alerts = inmet.find_alerts_by_city(3545803)

            self._state = 'on' if len(alerts) > 0 else 'off'

            self.attrs.clear()
            self.attrs[ATTR_DESCRIPTION] = alerts[0][ATTR_DESCRIPTION_INMET]
        except:
            self._available = False
            _LOGGER.exception(
                "Error retrieving data from InMet for sensor %s", self.name
            )
