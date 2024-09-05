"""Platform for sensor integration."""

from typing import Callable, Optional

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.core import HomeAssistant, callback
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    COORDINATOR,
    DOMAIN,
    FIELD_CREATED_AT,
    FIELD_DESCRIPTION,
    FIELD_FINISH,
    FIELD_FINISHED,
    FIELD_FUTURE,
    FIELD_ID,
    FIELD_ID_ALERT,
    FIELD_ID_SEVERITY,
    FIELD_INSTRUCTIONS,
    FIELD_RISKS,
    FIELD_SEQUENCE,
    FIELD_SEVERITY,
    FIELD_START,
    FIELD_UPDATED,
    FIELD_UPDATED_AT,
    FIELD_WARNING_COLOR,
    GEOCODE,
    NAME,
)
from .coordinator import InMetAlertsCoordinator

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {vol.Required("geocode"): cv.string, vol.Required("name"): cv.string}
)


async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the sensor platform."""
    # session = async_get_clientsession(hass)
    geocode = config["geocode"]
    name = config["name"]

    coordinator = InMetAlertsCoordinator(hass, {"geocode": geocode, "name": name})
    sensor = InMetAlertSensor(coordinator=coordinator)
    async_add_entities([sensor], update_before_add=True)


async def async_setup_entry(
    hass: HomeAssistant, config_entry, async_add_entities
) -> None:
    """Set up sensor platform."""
    entry_id: str = config_entry.entry_id

    coordinator = hass.data[DOMAIN][entry_id][COORDINATOR]
    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        InMetAlertSensor(coordinator, idx) for idx, ent in enumerate(coordinator.data)
    )


class InMetAlertSensor(CoordinatorEntity, SensorEntity):
    """An entity using CoordinatorEntity.

    The CoordinatorEntity class provides:
      should_poll
      async_update
      async_added_to_hass
      available

    """

    _attr_has_entity_name = True
    alerts: list | None

    def __init__(self, coordinator: InMetAlertsCoordinator) -> None:
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator, context=["sp", "1234"])

        config_data = coordinator.settings

        geocode = config_data[GEOCODE]

        self._attr_unique_id = f"inmet_{geocode}"
        self._attr_name = f"inmet_{geocode}"
        self._attr_icon = "mdi:home"
        self._attr_native_value = 0
        self._attr_unit_of_measurement = "alerts"
        self._attr_attribution = "Data provided by InMet"

        self.__reset_attributes()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        data = self.coordinator.data
        self._attr_native_value = data["state"]

        if self._attr_native_value > 0:
            raw_alerts = data["alerts"]
            alerts = []

            for raw_alert in raw_alerts:
                alert = {}
                inmet_id = raw_alert.get(FIELD_ID, None)
                alert["id"] = inmet_id
                alert["id_alert"] = raw_alert.get(FIELD_ID_ALERT, None)
                alert["sequence"] = raw_alert.get(FIELD_SEQUENCE, None)
                alert["updated"] = raw_alert.get(FIELD_UPDATED, False)
                alert["finished"] = raw_alert.get(FIELD_FINISHED, False)
                alert["created_at"] = raw_alert.get(FIELD_CREATED_AT, None)
                alert["updated_at"] = raw_alert.get(FIELD_UPDATED_AT, None)
                alert["start"] = raw_alert.get(FIELD_START, None)
                alert["end"] = raw_alert.get(FIELD_FINISH, None)
                alert["description"] = raw_alert.get(FIELD_DESCRIPTION, None)
                alert["warning_color"] = raw_alert.get(FIELD_WARNING_COLOR, None)
                alert["id_severity"] = raw_alert.get(FIELD_ID_SEVERITY, None)
                alert["severity"] = raw_alert.get(FIELD_SEVERITY, None)
                alert["risks"] = raw_alert.get(FIELD_RISKS, None)
                alert["instructions"] = raw_alert.get(FIELD_INSTRUCTIONS, None)
                alert["future"] = raw_alert.get(FIELD_FUTURE, False)
                alert["link"] = f"https://alertas2.inmet.gov.br/{inmet_id}"
                alerts.append(alert)

            self.alerts = alerts
            self._attr_icon = "mdi:home-alert"

        else:
            self.__reset_attributes()

        self.async_write_ha_state()

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return the state attributes."""
        attributes = {
            "alerts": self.alerts,
        }

        return attributes

    @property
    def unique_id(self) -> str:
        """Return the unique id."""

        return self._attr_unique_id

    def __reset_attributes(self):
        self.alerts = []
        self._attr_icon = "mdi:home"
        self._attr_native_value = 0
