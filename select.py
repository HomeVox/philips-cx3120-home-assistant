"""Select entities for Philips CX3120."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import PhilipsCX3120Runtime
from .const import (
    DOMAIN,
    PRESET_PATTERNS,
    TIMER_MAP,
    TIMER_OPTION_TO_VALUE,
    preset_from_status,
    timer_option_from_status,
)
from .entity import PhilipsCX3120Entity


@dataclass(frozen=True, kw_only=True)
class PhilipsCX3120SelectDescription(SelectEntityDescription):
    """Describe a CX3120 select entity."""

    current_option_fn: Callable[[dict[str, Any]], str | None]


SELECTS: tuple[PhilipsCX3120SelectDescription, ...] = (
    PhilipsCX3120SelectDescription(
        key="preset_control",
        name="Preset Control",
        icon="mdi:tune-variant",
        options=list(PRESET_PATTERNS.keys()),
        entity_category=EntityCategory.CONFIG,
        current_option_fn=preset_from_status,
    ),
    PhilipsCX3120SelectDescription(
        key="timer_control",
        name="Timer Control",
        icon="mdi:timer-edit-outline",
        options=list(TIMER_MAP.values()),
        entity_category=EntityCategory.CONFIG,
        current_option_fn=timer_option_from_status,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up select entities for a config entry."""
    runtime: PhilipsCX3120Runtime = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        PhilipsCX3120Select(runtime, entry, description) for description in SELECTS
    )


class PhilipsCX3120Select(PhilipsCX3120Entity, SelectEntity):
    """Select entity for Philips CX3120."""

    entity_description: PhilipsCX3120SelectDescription

    def __init__(
        self,
        runtime: PhilipsCX3120Runtime,
        entry: ConfigEntry,
        description: PhilipsCX3120SelectDescription,
    ) -> None:
        super().__init__(runtime, entry)
        self.entity_description = description
        device_id = str(self.coordinator.data.get("DeviceId", entry.entry_id))
        self._attr_unique_id = f"{device_id}-{description.key}"

    @property
    def current_option(self) -> str | None:
        """Return current option."""
        return self.entity_description.current_option_fn(self.coordinator.data)

    async def async_select_option(self, option: str) -> None:
        """Handle option selection."""
        if self.entity_description.key == "preset_control":
            await self.runtime.api.async_set_preset(option)
        else:
            await self.runtime.api.async_set_timer(TIMER_OPTION_TO_VALUE[option])
        await self.coordinator.async_request_refresh()
