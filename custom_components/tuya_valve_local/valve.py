"""Entité valve pour tuya_valve_local."""
from __future__ import annotations

import logging

from homeassistant.components.valve import (
    ValveDeviceClass,
    ValveEntity,
    ValveEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import TuyaValveCoordinator
from .const import (
    CONF_DEFAULT_DUR,
    CONF_NAME,
    DEFAULT_DURATION_S,
    DOMAIN,
    DPS_COUNTDOWN,
    DPS_VALVE,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    name = entry.data.get(CONF_NAME, "Vanne arrosage")
    async_add_entities([TuyaValveEntity(coordinator, entry, name)])


class TuyaValveEntity(CoordinatorEntity, ValveEntity):
    """Vanne d'arrosage Tuya locale."""

    _attr_device_class      = ValveDeviceClass.WATER
    _attr_supported_features = (
        ValveEntityFeature.OPEN | ValveEntityFeature.CLOSE
    )
    _attr_reports_position  = False

    def __init__(
        self,
        coordinator: TuyaValveCoordinator,
        entry: ConfigEntry,
        name: str,
    ) -> None:
        super().__init__(coordinator)
        self._entry    = entry
        self._dev_name = name
        self._attr_unique_id  = f"{DOMAIN}_{entry.entry_id}_valve"
        self._attr_name       = name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=name,
            manufacturer="Tuya",
            model="Vanne d'arrosage BLE",
        )

    @property
    def is_closed(self) -> bool | None:
        dps = self.coordinator.data or {}
        val = dps.get(DPS_VALVE)
        if val is None:
            return None
        return not val

    @property
    def is_opening(self) -> bool:
        return False

    @property
    def is_closing(self) -> bool:
        return False

    def _get_duration(self) -> int:
        """Récupère la durée depuis le number HA ou la valeur par défaut."""
        from homeassistant.helpers import entity_registry as er
        registry = er.async_get(self.hass)
        unique_id = f"{DOMAIN}_{self._entry.entry_id}_duration"
        entity_id = registry.async_get_entity_id("number", DOMAIN, unique_id)
        if entity_id:
            state = self.hass.states.get(entity_id)
            if state and state.state not in (None, "unavailable", "unknown"):
                try:
                    # Convertit minutes → secondes
                    return int(float(state.state) * 60)
                except ValueError:
                    pass
        # Valeur par défaut depuis la config
        return int(self._entry.data.get(CONF_DEFAULT_DUR, DEFAULT_DURATION_S))

    async def async_open_valve(self) -> None:
        """Ouvre la vanne : envoie DP11 (countdown) + DP1 (True) simultanément."""
        duration = self._get_duration()
        _LOGGER.debug("Ouverture vanne: countdown=%ds", duration)
        await self.coordinator.async_send_dps({
            DPS_COUNTDOWN: duration,
            DPS_VALVE:     True,
        })

    async def async_close_valve(self) -> None:
        """Ferme la vanne : DP1 = False."""
        await self.coordinator.async_send_dps({DPS_VALVE: False})
