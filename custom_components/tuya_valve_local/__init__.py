"""Tuya Valve Local — vanne d'arrosage via passerelle tinytuya."""
from __future__ import annotations

import logging
from datetime import timedelta

import tinytuya
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_DEVICE_ID,
    CONF_IP,
    CONF_LOCAL_KEY,
    CONF_NODE_ID,
    CONF_VERSION,
    DOMAIN,
    SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["valve", "number", "sensor", "select", "switch"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup de l'entrée."""
    coordinator = TuyaValveCoordinator(hass, entry)

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        raise ConfigEntryNotReady(f"Vanne injoignable: {err}") from err

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Décharge l'entrée."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


def _make_device(entry: ConfigEntry) -> tinytuya.Device:
    """Crée un Device tinytuya (avec node_id si passerelle)."""
    device_id = entry.data[CONF_DEVICE_ID]
    ip        = entry.data[CONF_IP]
    local_key = entry.data[CONF_LOCAL_KEY]
    version   = float(entry.data.get(CONF_VERSION, 3.3))
    node_id   = entry.data.get(CONF_NODE_ID, "").strip()

    if node_id:
        # Passerelle BLE : utilise Device standard avec cid (node_id)
        d = tinytuya.Device(device_id, ip, local_key, cid=node_id)
    else:
        d = tinytuya.Device(device_id, ip, local_key)

    d.set_version(version)
    d.set_socketTimeout(5)
    return d


class TuyaValveCoordinator(DataUpdateCoordinator):
    """Coordinator qui lit la vanne via tinytuya."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )
        self.entry = entry

    def _fetch(self) -> dict:
        d = _make_device(self.entry)
        result = d.status()
        if not result or "dps" not in result:
            raise UpdateFailed(f"Réponse invalide: {result}")
        # Normalise les clés en int
        return {int(k): v for k, v in result["dps"].items()
                if str(k).isdigit()}

    async def _async_update_data(self) -> dict:
        try:
            return await self.hass.async_add_executor_job(self._fetch)
        except Exception as err:
            raise UpdateFailed(f"Erreur lecture vanne: {err}") from err

    async def async_send_dps(self, dps: dict) -> None:
        """Envoie plusieurs DPS en une seule commande."""
        def _send():
            d = _make_device(self.entry)
            # Lecture préalable pour initialiser la session
            d.status()
            payload = d.generate_payload(
                tinytuya.CONTROL,
                {str(k): v for k, v in dps.items()},
            )
            result = d.send(payload)
            _LOGGER.debug("DPS envoyés %s → %s", dps, result)
            return result

        import asyncio
        await self.hass.async_add_executor_job(_send)
        await asyncio.sleep(1)
        await self.async_request_refresh()
