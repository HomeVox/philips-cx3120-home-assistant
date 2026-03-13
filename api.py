"""Local API wrapper for the Philips CX3120."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from aioairctrl import CoAPClient

from .const import (
    BEEP_OFF_VALUE,
    BEEP_ON_VALUE,
    KEY_BEEP,
    KEY_CHILD_LOCK,
    KEY_OSCILLATION,
    KEY_POWER,
    KEY_TARGET_TEMPERATURE,
    KEY_TIMER,
    OSCILLATION_OFF_VALUE,
    OSCILLATION_ON_VALUE,
    PRESET_PATTERNS,
)

_T = TypeVar("_T")


class PhilipsCX3120Api:
    """Thin async wrapper around aioairctrl's CoAP client."""

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self._client: CoAPClient | None = None

    async def async_disconnect(self) -> None:
        """Tear down the client connection."""
        if self._client is not None:
            await self._client.shutdown()
            self._client = None

    async def _async_ensure_client(self) -> CoAPClient:
        """Create client lazily."""
        if self._client is None:
            self._client = await CoAPClient.create(host=self.host, port=self.port)
        return self._client

    async def _async_execute(
        self,
        func: Callable[[CoAPClient], Awaitable[_T]],
        *,
        retry: bool = True,
    ) -> _T:
        """Execute a client call and reconnect once on failure."""
        client = await self._async_ensure_client()
        try:
            return await func(client)
        except Exception:
            await self.async_disconnect()
            if not retry:
                raise
            client = await self._async_ensure_client()
            return await func(client)

    async def async_get_status(self) -> dict[str, Any]:
        """Fetch raw device status."""

        async def _get_status(client: CoAPClient) -> dict[str, Any]:
            status, _max_age = await client.get_status()
            return status

        return await self._async_execute(_get_status)

    async def async_set_values(self, values: dict[str, Any]) -> bool:
        """Send raw control values to the device."""

        async def _set_values(client: CoAPClient) -> bool:
            return await client.set_control_values(values)

        return await self._async_execute(_set_values)

    async def async_set_power(self, enabled: bool) -> bool:
        """Turn the device on or off."""
        return await self.async_set_values({KEY_POWER: 1 if enabled else 0})

    async def async_set_preset(self, preset: str) -> bool:
        """Set one of the known CX3120 presets."""
        return await self.async_set_values(PRESET_PATTERNS[preset])

    async def async_set_target_temperature(self, temperature: int) -> bool:
        """Set target heater temperature."""
        return await self.async_set_values({KEY_TARGET_TEMPERATURE: temperature})

    async def async_set_child_lock(self, enabled: bool) -> bool:
        """Toggle child lock."""
        return await self.async_set_values({KEY_CHILD_LOCK: 1 if enabled else 0})

    async def async_set_beep(self, enabled: bool) -> bool:
        """Toggle keypad beep."""
        return await self.async_set_values({KEY_BEEP: BEEP_ON_VALUE if enabled else BEEP_OFF_VALUE})

    async def async_set_oscillation(self, enabled: bool) -> bool:
        """Toggle oscillation."""
        return await self.async_set_values(
            {KEY_OSCILLATION: OSCILLATION_ON_VALUE if enabled else OSCILLATION_OFF_VALUE}
        )

    async def async_set_timer(self, timer_value: int) -> bool:
        """Set the CX3120 shutdown timer."""
        return await self.async_set_values({KEY_TIMER: timer_value})
