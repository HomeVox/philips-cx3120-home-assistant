"""Binary sensors for Philips CX3120."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import PhilipsCX3120Runtime
from .const import DOMAIN, KEY_AUTO_PLUS_AI, KEY_ERROR_CODE, KEY_HEATING_ACTION
from .entity import PhilipsCX3120Entity


@dataclass(frozen=True, kw_only=True)
class PhilipsCX3120BinarySensorDescription(BinarySensorEntityDescription):
    """Describe a CX3120 binary sensor."""

    is_on_fn: Callable[[dict[str, Any]], bool]


BINARY_SENSORS: tuple[PhilipsCX3120BinarySensorDescription, ...] = (
    PhilipsCX3120BinarySensorDescription(
        key="problem",
        name="Problem",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=None,
        is_on_fn=lambda data: bool(data.get(KEY_ERROR_CODE, 0)),
    ),
    PhilipsCX3120BinarySensorDescription(
        key="heating",
        name="Heating",
        device_class=BinarySensorDeviceClass.HEAT,
        is_on_fn=lambda data: data.get(KEY_HEATING_ACTION) in {65, 67, 68},
    ),
    PhilipsCX3120BinarySensorDescription(
        key="auto_plus_ai",
        name="Auto Plus AI",
        icon="mdi:brain",
        is_on_fn=lambda data: data.get(KEY_AUTO_PLUS_AI) == 1,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensors for a config entry."""
    runtime: PhilipsCX3120Runtime = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        PhilipsCX3120BinarySensor(runtime, entry, description)
        for description in BINARY_SENSORS
    )


class PhilipsCX3120BinarySensor(PhilipsCX3120Entity, BinarySensorEntity):
    """Binary sensor for Philips CX3120."""

    entity_description: PhilipsCX3120BinarySensorDescription

    def __init__(
        self,
        runtime: PhilipsCX3120Runtime,
        entry: ConfigEntry,
        description: PhilipsCX3120BinarySensorDescription,
    ) -> None:
        super().__init__(runtime, entry)
        self.entity_description = description
        device_id = str(self.coordinator.data.get("DeviceId", entry.entry_id))
        self._attr_unique_id = f"{device_id}-{description.key}"

    @property
    def is_on(self) -> bool:
        """Return binary sensor state."""
        return self.entity_description.is_on_fn(self.coordinator.data)
