import asyncio
import json
from homeassistant import config_entries, core
from .const import (
    DOMAIN, CONF_IP, CONF_NAME, CONF_MAC
)
import logging
import subprocess
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryNotReady
_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    "switch",
    "binary_sensor",
]

async def async_setup(hass: core.HomeAssistant, config: dict):
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass, entry):
    _LOGGER.debug("Setting up My Device component")
    ip = entry.data.get('ip')
    name = entry.data.get('name')
    mac = entry.data.get('mac')

    result = subprocess.run(["ping", "-n", "1", "-w", "1000", ip], capture_output=True, text=True)

    if result.returncode == 0:
        status = "0"
    else:
        status = "-1"

    _LOGGER.debug(f"获取初始化信息完成，开始创建设备IP: {ip}, Name:{name}, Mac:{mac}, Status: {status}")

    coordinator = DEVICEDataUpdateCoordinator(hass, entry, ip, name, mac, status)

    await coordinator.async_refresh()
    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][ip] = coordinator

    _LOGGER.info(f"创建设备完成IP: {ip}, Name:{name}, Mac:{mac}, Status: {status}")

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setups(entry, [component])
        )

    return True

async def update_listener(hass, entry):
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: core.HomeAssistant, entry: config_entries.ConfigEntry):
    ip = entry.data.get(CONF_IP)
    # 卸载时清理对应的 coordinator 数据
    if ip and ip in hass.data[DOMAIN]:
        del hass.data[DOMAIN][ip]
        
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    return unload_ok

class DEVICEDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching DEVICE data."""

    def __init__(self, hass, entry, ip, name, mac, status):
        # 使用 update_interval 的代码

        self.hass = hass
        self.entry = entry

        self.ip = ip
        self.name = name
        self.mac = mac
        self.status = status

        self._isenable = True

        super().__init__(
            hass,
            _LOGGER,
            name=self.name,
            update_interval=timedelta(seconds=30),
        )

    def set_device_enabled(self, enabled):
        # 设置设备是否可用
        self._isenable = enabled

    async def _async_update_data(self):
        """Fetch data from My Custom Device."""
        try:
            # 通过ping检测设备在线状态
            result = await self.hass.async_add_executor_job(
                self._ping_device
            )
            self.status = "0" if result else "-1"
            return {
                "ip": self.ip,
                "name": self.name,
                "status": self.status
            }  
        except Exception as err:
            raise UpdateFailed(f"Error communicating with My Custom Device: {err}")

    def _ping_device(self):
        """同步执行ping检测"""
        try:
            result = subprocess.run(
                ["ping", "-n", "1", "-w", "2000", self.ip],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False
        except Exception as e:
            _LOGGER.error(f"Ping error: {e}")
            return False

        
