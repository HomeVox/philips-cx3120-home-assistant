"""Coordinator for Philips CX3120 polling."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import PhilipsCX3120Api
from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class PhilipsCX3120Coordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Poll the local CX3120 device over CoAP."""

    def __init__(self, hass: HomeAssistant, api: PhilipsCX3120Api) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from device."""
        try:
            return await self.api.async_get_status()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with Philips CX3120: {err}") from err
