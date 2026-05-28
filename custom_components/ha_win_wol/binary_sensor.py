"""Binary sensor platform for ha_win_wol."""
import logging
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the binary sensor platform."""
    ip = config_entry.data.get('ip')
    name = config_entry.data.get('name')
    
    coordinator = hass.data[DOMAIN][ip]
    
    # 创建状态传感器实体
    status_sensor = DeviceStatusBinarySensor(coordinator, hass, config_entry, ip, name)
    async_add_entities([status_sensor], False)


class DeviceStatusBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a device status binary sensor."""
    
    def __init__(self, coordinator, hass, entry, ip, name):
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.hass = hass
        self.entry = entry
        self._ip = ip
        self._name = name
        self._attr_name = f"{name} 状态"
        self._attr_unique_id = f"{ip}_status"
        
    @property
    def name(self):
        """Return the name of the binary sensor."""
        return self._attr_name
    
    @property
    def unique_id(self):
        """Return the unique id."""
        return self._attr_unique_id
    
    @property
    def is_on(self):
        """Return true if the binary sensor is on (device is online)."""
        if self.coordinator.data is None:
            return False
        return self.coordinator.data.get("status") == "0"
    
    @property
    def device_class(self):
        """Return the class of this device."""
        return "connectivity"
    
    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._ip)},
            "name": self._name,
            "manufacturer": "ha_win_wol",
            "model": "Wake on LAN Device",
        }
    
    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        last_update_str = ""
        if self.coordinator.last_update is not None:
            last_update_str = self.coordinator.last_update.isoformat()
        return {
            "ip": self._ip,
            "last_update": last_update_str,
        }
    
    async def async_added_to_hass(self):
        """When entity is added to hass."""
        await super().async_added_to_hass()
        # 监听coordinator更新
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
