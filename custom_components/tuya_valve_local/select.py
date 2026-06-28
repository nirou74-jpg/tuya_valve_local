"""Entité select (weather delay) pour tuya_valve_local."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import TuyaValveCoordinator
from .const import DOMAIN, DPS_WEATHER_DLY, WEATHER_DELAY_OPTIONS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([WeatherDelaySelect(coordinator, entry)])


class WeatherDelaySelect(CoordinatorEntity, SelectEntity):
    """Délai météo (weather delay)."""

    _attr_options         = WEATHER_DELAY_OPTIONS
    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon            = "mdi:weather-cloudy-clock"

    def __init__(self, coordinator: TuyaValveCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id  = f"{DOMAIN}_{entry.entry_id}_weather_delay"
        self._attr_name       = "Délai météo"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry.entry_id)})

    @property
    def current_option(self) -> str | None:
        return (self.coordinator.data or {}).get(DPS_WEATHER_DLY)

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_send_dps({DPS_WEATHER_DLY: option})
