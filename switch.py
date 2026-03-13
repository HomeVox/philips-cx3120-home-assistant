"""Switch platform for Philips CX3120."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import PhilipsCX3120Runtime
from .const import (
    BEEP_ON_VALUE,
    DOMAIN,
    KEY_BEEP,
    KEY_CHILD_LOCK,
)
from .entity import PhilipsCX3120Entity


@dataclass(frozen=True, kw_only=True)
class PhilipsCX3120SwitchDescription(SwitchEntityDescription):
    """Describe a CX3120 switch."""

    status_key: str


SWITCHES: tuple[PhilipsCX3120SwitchDescription, ...] = (
    PhilipsCX3120SwitchDescription(
        key="child_lock",
        name="Child Lock",
        icon="mdi:baby-face-outline",
        entity_category=EntityCategory.CONFIG,
        status_key=KEY_CHILD_LOCK,
    ),
    PhilipsCX3120SwitchDescription(
        key="beep",
        name="Beep",
        icon="mdi:volume-high",
        entity_category=EntityCategory.CONFIG,
        status_key=KEY_BEEP,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switches for a config entry."""
    runtime: PhilipsCX3120Runtime = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        PhilipsCX3120Switch(runtime, entry, description) for description in SWITCHES
    )


class PhilipsCX3120Switch(PhilipsCX3120Entity, SwitchEntity):
    """Switch entity for Philips CX3120."""

    entity_description: PhilipsCX3120SwitchDescription

    def __init__(
        self,
        runtime: PhilipsCX3120Runtime,
        entry: ConfigEntry,
        description: PhilipsCX3120SwitchDescription,
    ) -> None:
        super().__init__(runtime, entry)
        self.entity_description = description
        device_id = str(self.coordinator.data.get("DeviceId", entry.entry_id))
        self._attr_unique_id = f"{device_id}-{description.key}"

    @property
    def is_on(self) -> bool:
        """Return state of switch."""
        value = self.coordinator.data.get(self.entity_description.status_key)
        if self.entity_description.status_key == KEY_BEEP:
            return value == BEEP_ON_VALUE
        return value == 1

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on switch."""
        if self.entity_description.status_key == KEY_BEEP:
            await self.runtime.api.async_set_beep(True)
        else:
            await self.runtime.api.async_set_child_lock(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off switch."""
        if self.entity_description.status_key == KEY_BEEP:
            await self.runtime.api.async_set_beep(False)
        else:
            await self.runtime.api.async_set_child_lock(False)
        await self.coordinator.async_request_refresh()
