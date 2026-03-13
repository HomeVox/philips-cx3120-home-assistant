"""Diagnostics support for Philips CX3120."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

TO_REDACT = {
    "host",
    "DeviceId",
    "ProductId",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    runtime = hass.data[DOMAIN][entry.entry_id]
    status = runtime.coordinator.data or {}

    return {
        "entry": async_redact_data(entry.as_dict(), TO_REDACT),
        "status": async_redact_data(status, TO_REDACT),
    }
