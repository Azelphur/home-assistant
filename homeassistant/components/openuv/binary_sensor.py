"""Support for OpenUV binary sensors."""

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util.dt import as_local, parse_datetime, utcnow

from .const import DATA_PROTECTION_WINDOW, DOMAIN, LOGGER, TYPE_PROTECTION_WINDOW
from .coordinator import OpenUvCoordinator
from .entity import OpenUvEntity

ATTR_PROTECTION_WINDOW_ENDING_TIME = "end_time"
ATTR_PROTECTION_WINDOW_ENDING_UV = "end_uv"
ATTR_PROTECTION_WINDOW_STARTING_TIME = "start_time"
ATTR_PROTECTION_WINDOW_STARTING_UV = "start_uv"

BINARY_SENSOR_DESCRIPTION_PROTECTION_WINDOW = BinarySensorEntityDescription(
    key=TYPE_PROTECTION_WINDOW,
    translation_key="protection_window",
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    # Once we've successfully authenticated, we re-enable client request retries:
    """Set up an OpenUV sensor based on a config entry."""
    coordinators: dict[str, OpenUvCoordinator] = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            OpenUvBinarySensor(
                coordinators[DATA_PROTECTION_WINDOW],
                BINARY_SENSOR_DESCRIPTION_PROTECTION_WINDOW,
            )
        ]
    )


class OpenUvBinarySensor(OpenUvEntity, BinarySensorEntity):
    """Define a binary sensor for OpenUV."""

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update the entity from the latest data."""
        self._update_attrs()
        super()._handle_coordinator_update()

    def _update_attrs(self) -> None:
        data = self.coordinator.data

        for key in ("from_time", "to_time", "from_uv", "to_uv"):
            if not data.get(key):
                LOGGER.warning("Skipping update due to missing data: %s", key)
                return

        if self.entity_description.key == TYPE_PROTECTION_WINDOW:
            from_dt = parse_datetime(data["from_time"])
            to_dt = parse_datetime(data["to_time"])

            if not from_dt or not to_dt:
                LOGGER.warning(
                    "Unable to parse protection window datetimes: %s, %s",
                    data["from_time"],
                    data["to_time"],
                )
                self._attr_is_on = False
                return

            self._attr_is_on = from_dt <= utcnow() <= to_dt
            self._attr_extra_state_attributes.update(
                {
                    ATTR_PROTECTION_WINDOW_ENDING_TIME: as_local(to_dt),
                    ATTR_PROTECTION_WINDOW_ENDING_UV: data["to_uv"],
                    ATTR_PROTECTION_WINDOW_STARTING_UV: data["from_uv"],
                    ATTR_PROTECTION_WINDOW_STARTING_TIME: as_local(from_dt),
                }
            )
