import logging
from datetime import datetime, timedelta

from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# WOL 发送后乐观状态持续时间（秒），设备启动期间开关保持"打开"
WOL_PENDING_SECONDS = 60


async def async_setup_entry(hass, config_entry, async_add_entities):
    ip = config_entry.data.get("ip")
    name = config_entry.data.get("name")
    mac = config_entry.data.get("mac")

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
        # 乐观状态：WOL 发送后标记时间，60 秒内认为设备在线
        self._wol_pending_since = None

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
        # 优先用 coordinator 实时状态（ping 结果）
        if self.coordinator.data is not None:
            coordinator_online = self.coordinator.data.get("status") == "0"
        else:
            coordinator_online = False

        # WOL 乐观状态：发送后 60 秒内，即使 ping 失败也认为在线
        if self._wol_pending_since is not None:
            elapsed = (datetime.now() - self._wol_pending_since).total_seconds()
            if elapsed < WOL_PENDING_SECONDS:
                return True  # 乐观在线
            else:
                # 60 秒已过，清除待处理标记，回归 ping 状态
                self._wol_pending_since = None

        return coordinator_online

    async def async_turn_on(self, **kwargs):
        """Turn the switch on: send WOL packet."""
        _LOGGER.debug("设备的 ip: %s", self._ip)

        from wakeonlan import send_magic_packet
        send_magic_packet(self._mac.strip().upper())

        # 设置乐观状态：60 秒内开关保持打开，等待设备启动响应 ping
        self._wol_pending_since = datetime.now()
        self.async_write_ha_state()

        _LOGGER.debug("---------------switch async_turn_on----------------")

        # 通知 coordinator 刷新状态（设备启动后 ping 成功会更新状态）
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        # 清除 WOL 待处理状态
        self._wol_pending_since = None
        self.async_write_ha_state()

        _LOGGER.debug("---------------switch async_turn_off----------------")
        await self.coordinator.async_request_refresh()
