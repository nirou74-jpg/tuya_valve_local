"""Entité switch (smart weather) pour tuya_valve_local."""
from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import TuyaValveCoordinator
from .const import DOMAIN, DPS_SMART_WX

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SmartWeatherSwitch(coordinator, entry)])


class SmartWeatherSwitch(CoordinatorEntity, SwitchEntity):
    """Switch smart weather."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon            = "mdi:sun-wireless"

    def __init__(self, coordinator: TuyaValveCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id  = f"{DOMAIN}_{entry.entry_id}_smart_weather"
        self._attr_name       = "Smart weather"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry.entry_id)})

    @property
    def is_on(self) -> bool | None:
        val = (self.coordinator.data or {}).get(DPS_SMART_WX)
        if val is None:
            return None
        return bool(val)

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_send_dps({DPS_SMART_WX: True})

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_send_dps({DPS_SMART_WX: False})
