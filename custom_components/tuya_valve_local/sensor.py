"""Capteurs pour tuya_valve_local."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import TuyaValveCoordinator
from .const import (
    DOMAIN,
    DPS_ACCUM_TIME,
    DPS_BATTERY,
    DPS_COUNTDOWN,
    DPS_LAST_TIME,
    DPS_OPERATION,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        BatterySensor(coordinator, entry),
        OperationSensor(coordinator, entry),
        AccumTimeSensor(coordinator, entry),
        LastTimeSensor(coordinator, entry),
        CountdownSensor(coordinator, entry),
    ])


def _device_info(entry: ConfigEntry) -> DeviceInfo:
    return DeviceInfo(identifiers={(DOMAIN, entry.entry_id)})


class ValveBaseSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry, unique_suffix, name, dps_id):
        super().__init__(coordinator)
        self._dps_id = dps_id
        self._attr_unique_id   = f"{DOMAIN}_{entry.entry_id}_{unique_suffix}"
        self._attr_name        = name
        self._attr_device_info = _device_info(entry)

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get(self._dps_id)


class BatterySensor(ValveBaseSensor):
    _attr_device_class  = SensorDeviceClass.BATTERY
    _attr_state_class   = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "battery", "Batterie", DPS_BATTERY)


class OperationSensor(ValveBaseSensor):
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:information"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "operation", "Opération", DPS_OPERATION)


class AccumTimeSensor(ValveBaseSensor):
    _attr_device_class  = SensorDeviceClass.DURATION
    _attr_state_class   = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:timer-sand"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "accum_time", "Temps cumulé", DPS_ACCUM_TIME)


class LastTimeSensor(ValveBaseSensor):
    _attr_device_class  = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:history"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "last_time", "Dernier usage", DPS_LAST_TIME)


class CountdownSensor(ValveBaseSensor):
    _attr_device_class  = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_icon = "mdi:timer-outline"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "countdown", "Countdown", DPS_COUNTDOWN)
