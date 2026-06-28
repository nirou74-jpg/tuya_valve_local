"""Entité number (durée arrosage) pour tuya_valve_local."""
from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import TuyaValveCoordinator
from .const import CONF_DEFAULT_DUR, DEFAULT_DURATION_S, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([ValveDurationNumber(coordinator, entry)])


class ValveDurationNumber(CoordinatorEntity, NumberEntity, RestoreEntity):
    """Durée d'arrosage en minutes."""

    _attr_native_min_value = 1
    _attr_native_max_value = 1440
    _attr_native_step      = 1
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_mode             = NumberMode.BOX
    _attr_entity_category  = EntityCategory.CONFIG
    _attr_icon             = "mdi:timer-water"
    _attr_suggested_display_precision = 0

    def __init__(self, coordinator: TuyaValveCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        # Durée par défaut depuis la config (en secondes → minutes)
        default_s = int(entry.data.get(CONF_DEFAULT_DUR, DEFAULT_DURATION_S))
        self._value = default_s / 60.0
        self._attr_unique_id  = f"{DOMAIN}_{entry.entry_id}_duration"
        self._attr_name       = "Durée d'arrosage"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
        )

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last = await self.async_get_last_state()
        if last and last.state not in (None, "unavailable", "unknown"):
            try:
                self._value = float(last.state)
            except ValueError:
                pass

    @property
    def native_value(self) -> float:
        return self._value

    async def async_set_native_value(self, value: float) -> None:
        self._value = value
        self.async_write_ha_state()
