import logging
from homeassistant.components.switch import SwitchEntity
from .const import (
    DOMAIN, 
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    ip = config_entry.data.get('ip')
    name = config_entry.data.get('name')
    mac = config_entry.data.get('mac')

    coordinator = hass.data[DOMAIN][ip]
    my_switch = MyCustomSwitch(coordinator, hass, config_entry, ip, name, mac)
    async_add_entities([my_switch], False) 
        
class MyCustomSwitch(SwitchEntity):
    def __init__(self, coordinator, hass, entry, ip, name, mac):
        super().__init__()
        self.coordinator = coordinator
        self.hass = hass
        self.entry = entry
        self._ip = ip
        self._name = name
        self._mac = mac
        if self.coordinator.data["status"] == "0":
            self._state = True
        else:        
            self._state = False
    
    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._ip

    @property
    def device_info(self):
        _LOGGER.debug("Data will be update every %s", self.coordinator.data)
        return {
            "identifiers": {(DOMAIN, self._ip)},
            "name": self._name,
            "manufacturer": "ha_win_wol",
            "model": "Wake on LAN Device",
        }
    
    @property
    def is_on(self):
        """Return true if the switch is on."""
        if self.coordinator.data is None:
            return self._state
        return self.coordinator.data.get("status") == "0"
    
    async def set_state(self, state):
        self._state = state

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        self._state = True
        self.schedule_update_ha_state()
        _LOGGER.debug(f"设备的ip: {self._ip}")

        from wakeonlan import send_magic_packet
        send_magic_packet(self._mac.strip().upper())

        _LOGGER.debug("---------------switch async_turn_on----------------")
        
        # 触发coordinator更新状态
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        self._state = False
        self.schedule_update_ha_state()
        _LOGGER.debug(f"设备的deviceno: {self._ip}")
       
        _LOGGER.debug("---------------switch async_turn_off----------------")
        
        # 触发coordinator更新状态
        await self.coordinator.async_request_refresh()

