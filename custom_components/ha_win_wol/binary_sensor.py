"""Binary sensor platform for ha_win_wol."""
import logging

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the binary sensor platform."""
    ip = config_entry.data.get("ip")
    name = config_entry.data.get("name")

    coordinator = hass.data.get(DOMAIN, {}).get(ip)
    if coordinator is None:
        _LOGGER.error("Coordinator not found for IP: %s", ip)
        return

    _LOGGER.debug("Setting up binary sensor for %s (%s)", name, ip)
    status_sensor = DeviceStatusBinarySensor(coordinator, ip, name)
    async_add_entities([status_sensor], False)


class DeviceStatusBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a device status binary sensor."""

    def __init__(self, coordinator, ip, name):
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._attr_name = f"{name} 状态"
        self._attr_unique_id = f"{ip}_status"
        self._attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    @property
    def is_on(self):
        """Return true if the device is online."""
        # 直接读取 coordinator 实时状态，避免使用已过期的缓存
        data = self.coordinator.data
        if data is None:
            return False
        return data.get("status") == "0"

    @property
    def device_info(self):
        """Return device information."""
        data = self.coordinator.data
        return {
            "identifiers": {(DOMAIN, data.get("ip") if data else self.entity_id)},
            "name": data.get("name") if data else self._attr_name,
            "manufacturer": "ha_win_wol",
            "model": "Wake on LAN Device",
        }

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attrs = {}
        data = self.coordinator.data
        if data is not None:
            attrs["ip"] = data.get("ip")
        # 使用 coordinator 维护的时间戳
        if self.coordinator._last_updated is not None:
            attrs["last_update"] = self.coordinator._last_updated.isoformat()
        return attrs
