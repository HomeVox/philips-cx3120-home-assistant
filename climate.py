"""Climate platform for Philips CX3120."""

from __future__ import annotations

from typing import Any

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
    SWING_OFF,
    SWING_ON,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import PhilipsCX3120Runtime
from .const import (
    DOMAIN,
    KEY_HEATING_ACTION,
    KEY_OSCILLATION,
    KEY_POWER,
    KEY_TARGET_TEMPERATURE,
    OSCILLATION_OFF_VALUE,
    PRESET_AUTO_PLUS,
    PRESET_PATTERNS,
    PRESET_VENTILATION,
    current_temperature_from_status,
    preset_from_status,
)
from .entity import PhilipsCX3120Entity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up climate entity from config entry."""
    runtime: PhilipsCX3120Runtime = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([PhilipsCX3120ClimateEntity(runtime, entry)])


class PhilipsCX3120ClimateEntity(PhilipsCX3120Entity, ClimateEntity):
    """Philips CX3120 climate entity."""

    _attr_name = None
    _attr_translation_key = "heater"
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.AUTO, HVACMode.HEAT, HVACMode.FAN_ONLY]
    _attr_preset_modes = list(PRESET_PATTERNS.keys())
    _attr_swing_modes = [SWING_OFF, SWING_ON]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.SWING_MODE
    )
    _attr_min_temp = 1
    _attr_max_temp = 37
    _attr_target_temperature_step = 1

    def __init__(self, runtime: PhilipsCX3120Runtime, entry: ConfigEntry) -> None:
        super().__init__(runtime, entry)
        device_id = str(self.coordinator.data.get("DeviceId", entry.entry_id))
        self._attr_unique_id = f"{device_id}-climate"

    @property
    def current_temperature(self) -> float | None:
        """Return current temperature."""
        return current_temperature_from_status(self.coordinator.data)

    @property
    def target_temperature(self) -> float | None:
        """Return target temperature."""
        value = self.coordinator.data.get(KEY_TARGET_TEMPERATURE)
        if value is None:
            return None
        return float(value)

    @property
    def preset_mode(self) -> str | None:
        """Return active preset."""
        return preset_from_status(self.coordinator.data)

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return current hvac mode."""
        if self.coordinator.data.get(KEY_POWER) != 1:
            return HVACMode.OFF

        preset = self.preset_mode
        if preset == PRESET_AUTO_PLUS:
            return HVACMode.AUTO
        if preset == PRESET_VENTILATION:
            return HVACMode.FAN_ONLY
        return HVACMode.HEAT

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return current hvac action."""
        if self.coordinator.data.get(KEY_POWER) != 1:
            return HVACAction.OFF

        raw_action = self.coordinator.data.get(KEY_HEATING_ACTION)
        if raw_action == 0:
            return HVACAction.FAN
        if raw_action == -16:
            return HVACAction.IDLE
        if isinstance(raw_action, int):
            return HVACAction.HEATING
        return None

    @property
    def swing_mode(self) -> str | None:
        """Return swing mode."""
        if self.coordinator.data.get(KEY_OSCILLATION, OSCILLATION_OFF_VALUE) == OSCILLATION_OFF_VALUE:
            return SWING_OFF
        return SWING_ON

    async def async_turn_on(self) -> None:
        """Turn device on."""
        await self.runtime.api.async_set_power(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn device off."""
        await self.runtime.api.async_set_power(False)
        await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set HVAC mode."""
        if hvac_mode == HVACMode.OFF:
            await self.async_turn_off()
            return
        if hvac_mode == HVACMode.AUTO:
            await self.async_set_preset_mode(PRESET_AUTO_PLUS)
            return
        if hvac_mode == HVACMode.FAN_ONLY:
            await self.async_set_preset_mode(PRESET_VENTILATION)
            return
        await self.async_set_preset_mode("low")

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set preset mode."""
        if preset_mode not in PRESET_PATTERNS:
            return
        await self.runtime.api.async_set_preset(preset_mode)
        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set target temperature."""
        raw_temperature = kwargs.get("temperature")
        if raw_temperature is None:
            return
        temperature = int(raw_temperature)
        temperature = max(self._attr_min_temp, min(temperature, self._attr_max_temp))
        await self.runtime.api.async_set_target_temperature(temperature)
        await self.coordinator.async_request_refresh()

    async def async_set_swing_mode(self, swing_mode: str) -> None:
        """Set oscillation on/off."""
        await self.runtime.api.async_set_oscillation(swing_mode == SWING_ON)
        await self.coordinator.async_request_refresh()
