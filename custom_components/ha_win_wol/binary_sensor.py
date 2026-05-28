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
        if self.coordinator.data is None:
            return False
        return self.coordinator.data.get("status") == "0"

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.data.get("ip"))},
            "name": self.coordinator.data.get("name"),
            "manufacturer": "ha_win_wol",
            "model": "Wake on LAN Device",
        }

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attrs = {"ip": self.coordinator.data.get("ip")}
        if self.coordinator._last_updated is not None:
            attrs["last_update"] = self.coordinator._last_updated.isoformat()
        return attrs
