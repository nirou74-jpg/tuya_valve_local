"""Config flow pour tuya_valve_local."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries

from .const import (
    CONF_DEFAULT_DUR,
    CONF_DEVICE_ID,
    CONF_IP,
    CONF_LOCAL_KEY,
    CONF_NAME,
    CONF_NODE_ID,
    CONF_VERSION,
    DEFAULT_DURATION_S,
    DOMAIN,
    PROTOCOL_VERSIONS,
)


class TuyaValveLocalConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow pour tuya_valve_local."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            if not user_input[CONF_DEVICE_ID].strip():
                errors[CONF_DEVICE_ID] = "device_id_required"
            elif not user_input[CONF_IP].strip():
                errors[CONF_IP] = "ip_required"
            elif not user_input[CONF_LOCAL_KEY].strip():
                errors[CONF_LOCAL_KEY] = "local_key_required"
            else:
                node_id = user_input.get(CONF_NODE_ID, "").strip()
                unique = f"{user_input[CONF_DEVICE_ID]}_{node_id}" if node_id else user_input[CONF_DEVICE_ID]
                await self.async_set_unique_id(unique)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, "Vanne arrosage"),
                    data=user_input,
                )

        schema = vol.Schema({
            vol.Required(CONF_NAME,        default="Vanne arrosage"): str,
            vol.Required(CONF_DEVICE_ID,   default=""): str,
            vol.Required(CONF_IP,          default=""): str,
            vol.Required(CONF_LOCAL_KEY,   default=""): str,
            vol.Optional(CONF_NODE_ID,     default=""): str,
            vol.Required(CONF_VERSION,     default="3.3"):
                vol.In(PROTOCOL_VERSIONS),
            vol.Required(CONF_DEFAULT_DUR, default=DEFAULT_DURATION_S): int,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
