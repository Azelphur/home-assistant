"""Sensor platform for La Marzocco espresso machines."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import cast

from pylamarzocco.const import BackFlushStatus, ModelName, WidgetType
from pylamarzocco.models import (
    BackFlush,
    BaseWidgetOutput,
    CoffeeAndFlushCounter,
    CoffeeBoiler,
    MachineStatus,
    SteamBoilerLevel,
    SteamBoilerTemperature,
)

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType

from .coordinator import LaMarzoccoConfigEntry
from .entity import LaMarzoccoEntity, LaMarzoccoEntityDescription

# Coordinator is used to centralize the data updates
PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class LaMarzoccoSensorEntityDescription(
    LaMarzoccoEntityDescription,
    SensorEntityDescription,
):
    """Description of a La Marzocco sensor."""

    value_fn: Callable[
        [dict[WidgetType, BaseWidgetOutput]], StateType | datetime | None
    ]


ENTITIES: tuple[LaMarzoccoSensorEntityDescription, ...] = (
    LaMarzoccoSensorEntityDescription(
        key="coffee_boiler_ready_time",
        translation_key="coffee_boiler_ready_time",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=(
            lambda config: cast(
                CoffeeBoiler, config[WidgetType.CM_COFFEE_BOILER]
            ).ready_start_time
        ),
        entity_category=EntityCategory.DIAGNOSTIC,
        available_fn=(
            lambda coordinator: WidgetType.CM_COFFEE_BOILER
            in coordinator.device.dashboard.config
        ),
    ),
    LaMarzoccoSensorEntityDescription(
        key="steam_boiler_ready_time",
        translation_key="steam_boiler_ready_time",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=(
            lambda config: cast(
                SteamBoilerLevel, config[WidgetType.CM_STEAM_BOILER_LEVEL]
            ).ready_start_time
        ),
        entity_category=EntityCategory.DIAGNOSTIC,
        supported_fn=(
            lambda coordinator: coordinator.device.dashboard.model_name
            in (ModelName.LINEA_MICRA, ModelName.LINEA_MINI_R)
        ),
    ),
    LaMarzoccoSensorEntityDescription(
        key="brewing_start_time",
        translation_key="brewing_start_time",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=(
            lambda config: cast(
                MachineStatus, config[WidgetType.CM_MACHINE_STATUS]
            ).brewing_start_time
        ),
        entity_category=EntityCategory.DIAGNOSTIC,
        available_fn=(lambda coordinator: not coordinator.websocket_terminated),
    ),
    LaMarzoccoSensorEntityDescription(
        key="steam_boiler_ready_time",
        translation_key="steam_boiler_ready_time",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=(
            lambda config: cast(
                SteamBoilerTemperature, config[WidgetType.CM_STEAM_BOILER_TEMPERATURE]
            ).ready_start_time
        ),
        entity_category=EntityCategory.DIAGNOSTIC,
        supported_fn=(
            lambda coordinator: coordinator.device.dashboard.model_name
            in (ModelName.GS3_AV, ModelName.GS3_MP, ModelName.LINEA_MINI)
        ),
    ),
    LaMarzoccoSensorEntityDescription(
        key="last_cleaning_time",
        translation_key="last_cleaning_time",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=(
            lambda config: cast(
                BackFlush,
                config.get(
                    WidgetType.CM_BACK_FLUSH, BackFlush(status=BackFlushStatus.OFF)
                ),
            ).last_cleaning_start_time
        ),
        entity_category=EntityCategory.DIAGNOSTIC,
        supported_fn=(
            lambda coordinator: coordinator.device.dashboard.model_name
            is not ModelName.GS3_MP
        ),
    ),
)

STATISTIC_ENTITIES: tuple[LaMarzoccoSensorEntityDescription, ...] = (
    LaMarzoccoSensorEntityDescription(
        key="drink_stats_coffee",
        translation_key="total_coffees_made",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=(
            lambda statistics: cast(
                CoffeeAndFlushCounter, statistics[WidgetType.COFFEE_AND_FLUSH_COUNTER]
            ).total_coffee
        ),
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    LaMarzoccoSensorEntityDescription(
        key="drink_stats_flushing",
        translation_key="total_flushes_done",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=(
            lambda statistics: cast(
                CoffeeAndFlushCounter, statistics[WidgetType.COFFEE_AND_FLUSH_COUNTER]
            ).total_flush
        ),
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LaMarzoccoConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up sensor entities."""
    config_coordinator = entry.runtime_data.config_coordinator
    statistic_coordinators = entry.runtime_data.statistics_coordinator

    entities = [
        LaMarzoccoSensorEntity(config_coordinator, description)
        for description in ENTITIES
        if description.supported_fn(config_coordinator)
    ]
    entities.extend(
        LaMarzoccoStatisticSensorEntity(statistic_coordinators, description)
        for description in STATISTIC_ENTITIES
        if description.supported_fn(statistic_coordinators)
    )
    async_add_entities(entities)


class LaMarzoccoSensorEntity(LaMarzoccoEntity, SensorEntity):
    """Sensor for La Marzocco."""

    entity_description: LaMarzoccoSensorEntityDescription

    @property
    def native_value(self) -> StateType | datetime | None:
        """Return  value of the sensor."""
        return self.entity_description.value_fn(
            self.coordinator.device.dashboard.config
        )


class LaMarzoccoStatisticSensorEntity(LaMarzoccoSensorEntity):
    """Sensor for La Marzocco statistics."""

    @property
    def native_value(self) -> StateType | datetime | None:
        """Return the value of the sensor."""
        return self.entity_description.value_fn(
            self.coordinator.device.statistics.widgets
        )
