"""Config flow for Philips CX3120."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow

from .api import PhilipsCX3120Api
from .const import CONF_HOST, CONF_NAME, CONF_PORT, DEFAULT_NAME, DEFAULT_PORT, DOMAIN, KEY_DEVICE_ID, title_from_status

_LOGGER = logging.getLogger(__name__)


class PhilipsCX3120ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Philips CX3120."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            port = int(user_input[CONF_PORT])
            configured_name = user_input.get(CONF_NAME, "").strip()

            self._async_abort_entries_match({CONF_HOST: host})

            api = PhilipsCX3120Api(host=host, port=port)
            try:
                async with asyncio.timeout(15):
                    status = await api.async_get_status()
            except TimeoutError:
                errors["base"] = "cannot_connect"
            except Exception as err:  # noqa: BLE001
                _LOGGER.debug("Unable to connect to CX3120 at %s:%s: %s", host, port, err)
                errors["base"] = "cannot_connect"
            else:
                unique_id = str(status.get(KEY_DEVICE_ID) or host)
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                title = configured_name or title_from_status(status, DEFAULT_NAME)
                return self.async_create_entry(
                    title=title,
                    data={
                        CONF_HOST: host,
                        CONF_PORT: port,
                        CONF_NAME: title,
                    },
                )
            finally:
                await api.async_disconnect()

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=""): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
