"""Number entities for Philips CX3120."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import PhilipsCX3120Runtime
from .const import DOMAIN, KEY_TARGET_TEMPERATURE
from .entity import PhilipsCX3120Entity


@dataclass(frozen=True, kw_only=True)
class PhilipsCX3120NumberDescription(NumberEntityDescription):
    """Describe a CX3120 number entity."""


TARGET_TEMPERATURE = PhilipsCX3120NumberDescription(
    key="target_temperature_control",
    name="Target Temperature Control",
    native_min_value=1,
    native_max_value=37,
    native_step=1,
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    mode=NumberMode.BOX,
    icon="mdi:thermometer-chevron-up",
    entity_category=EntityCategory.CONFIG,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number entities for a config entry."""
    runtime: PhilipsCX3120Runtime = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([PhilipsCX3120TargetTemperatureNumber(runtime, entry)])


class PhilipsCX3120TargetTemperatureNumber(PhilipsCX3120Entity, NumberEntity):
    """Number entity for target temperature."""

    entity_description = TARGET_TEMPERATURE

    def __init__(self, runtime: PhilipsCX3120Runtime, entry: ConfigEntry) -> None:
        super().__init__(runtime, entry)
        device_id = str(self.coordinator.data.get("DeviceId", entry.entry_id))
        self._attr_unique_id = f"{device_id}-{self.entity_description.key}"

    @property
    def native_value(self) -> float | None:
        """Return current target temperature."""
        value = self.coordinator.data.get(KEY_TARGET_TEMPERATURE)
        if value is None:
            return None
        return float(value)

    async def async_set_native_value(self, value: float) -> None:
        """Set target temperature."""
        await self.runtime.api.async_set_target_temperature(int(value))
        await self.coordinator.async_request_refresh()
