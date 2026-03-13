"""Philips CX3120 integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import PhilipsCX3120Api
from .const import CONF_HOST, CONF_PORT, DOMAIN, PLATFORMS
from .coordinator import PhilipsCX3120Coordinator


@dataclass
class PhilipsCX3120Runtime:
    """Runtime data for a config entry."""

    api: PhilipsCX3120Api
    coordinator: PhilipsCX3120Coordinator


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up via YAML."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Philips CX3120 from config entry."""
    hass.data.setdefault(DOMAIN, {})

    api = PhilipsCX3120Api(
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
    )
    coordinator = PhilipsCX3120Coordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = PhilipsCX3120Runtime(
        api=api,
        coordinator=coordinator,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if not unload_ok:
        return False

    runtime: PhilipsCX3120Runtime = hass.data[DOMAIN].pop(entry.entry_id)
    await runtime.api.async_disconnect()

    if not hass.data[DOMAIN]:
        hass.data.pop(DOMAIN)

    return True
