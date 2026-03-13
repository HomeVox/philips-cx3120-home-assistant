"""Sensor platform for Philips CX3120."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import PhilipsCX3120Runtime
from .const import (
    DOMAIN,
    KEY_CONNECT_TYPE,
    KEY_ERROR_CODE,
    KEY_FREE_MEMORY,
    KEY_REMAINING_TIME,
    KEY_RSSI,
    KEY_RUNTIME,
    KEY_WIFI_VERSION,
    current_temperature_from_status,
    heating_action_from_status,
    preset_from_status,
    timer_option_from_status,
)
from .entity import PhilipsCX3120Entity


@dataclass(frozen=True, kw_only=True)
class PhilipsCX3120SensorDescription(SensorEntityDescription):
    """Describe a CX3120 sensor."""

    value_fn: Callable[[dict[str, Any]], Any]


SENSORS: tuple[PhilipsCX3120SensorDescription, ...] = (
    PhilipsCX3120SensorDescription(
        key="current_temperature",
        name="Current Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=current_temperature_from_status,
    ),
    PhilipsCX3120SensorDescription(
        key="heating_action",
        name="Heating Action",
        icon="mdi:radiator",
        value_fn=heating_action_from_status,
    ),
    PhilipsCX3120SensorDescription(
        key="preset",
        name="Preset",
        icon="mdi:creation",
        value_fn=preset_from_status,
    ),
    PhilipsCX3120SensorDescription(
        key="wifi_signal",
        name="WiFi Signal",
        native_unit_of_measurement="dBm",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:wifi",
        value_fn=lambda data: data.get(KEY_RSSI),
    ),
    PhilipsCX3120SensorDescription(
        key="error_code",
        name="Error Code",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:alert-circle-outline",
        value_fn=lambda data: data.get(KEY_ERROR_CODE),
    ),
    PhilipsCX3120SensorDescription(
        key="runtime",
        name="Runtime",
        native_unit_of_measurement="s",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:timer-outline",
        value_fn=lambda data: data.get(KEY_RUNTIME),
    ),
    PhilipsCX3120SensorDescription(
        key="timer",
        name="Timer",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:timer-cog-outline",
        value_fn=timer_option_from_status,
    ),
    PhilipsCX3120SensorDescription(
        key="remaining_time",
        name="Remaining Time",
        native_unit_of_measurement="h",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:timer-sand",
        value_fn=lambda data: data.get(KEY_REMAINING_TIME),
    ),
    PhilipsCX3120SensorDescription(
        key="connect_type",
        name="Connect Type",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:lan-connect",
        value_fn=lambda data: data.get(KEY_CONNECT_TYPE),
    ),
    PhilipsCX3120SensorDescription(
        key="wifi_version",
        name="WiFi Version",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:chip",
        value_fn=lambda data: data.get(KEY_WIFI_VERSION),
    ),
    PhilipsCX3120SensorDescription(
        key="free_memory",
        name="Free Memory",
        native_unit_of_measurement="B",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:memory",
        value_fn=lambda data: data.get(KEY_FREE_MEMORY),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors for a config entry."""
    runtime: PhilipsCX3120Runtime = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        PhilipsCX3120Sensor(runtime, entry, description) for description in SENSORS
    )


class PhilipsCX3120Sensor(PhilipsCX3120Entity, SensorEntity):
    """Sensor entity for Philips CX3120."""

    entity_description: PhilipsCX3120SensorDescription

    def __init__(
        self,
        runtime: PhilipsCX3120Runtime,
        entry: ConfigEntry,
        description: PhilipsCX3120SensorDescription,
    ) -> None:
        super().__init__(runtime, entry)
        self.entity_description = description
        device_id = str(self.coordinator.data.get("DeviceId", entry.entry_id))
        self._attr_unique_id = f"{device_id}-{description.key}"

    @property
    def native_value(self) -> Any:
        """Return entity value."""
        return self.entity_description.value_fn(self.coordinator.data)
