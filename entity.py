"""Shared entity helpers for Philips CX3120."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import PhilipsCX3120Runtime
from .const import CONF_NAME, DOMAIN, KEY_DEVICE_ID, KEY_MODEL, KEY_NAME, KEY_SW_VERSION, MANUFACTURER, MODEL


class PhilipsCX3120Entity(CoordinatorEntity):
    """Base entity class for the CX3120 integration."""

    _attr_has_entity_name = True

    def __init__(self, runtime: PhilipsCX3120Runtime, entry: ConfigEntry) -> None:
        super().__init__(runtime.coordinator)
        self.runtime = runtime
        self.entry = entry

    @property
    def device_info(self) -> DeviceInfo:
        """Return shared device metadata."""
        status = self.coordinator.data or {}
        device_id = str(status.get(KEY_DEVICE_ID) or self.entry.entry_id)
        return DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            manufacturer=MANUFACTURER,
            model=str(status.get(KEY_MODEL) or MODEL),
            name=str(status.get(KEY_NAME) or self.entry.data.get(CONF_NAME)),
            sw_version=str(status.get(KEY_SW_VERSION) or ""),
        )
