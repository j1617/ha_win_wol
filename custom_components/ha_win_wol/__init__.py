import asyncio
import json
from homeassistant import config_entries, core
from .const import DOMAIN, CONF_IP, CONF_NAME, CONF_MAC
import logging
from datetime import datetime, timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryNotReady
import ping3

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    "switch",
    "binary_sensor",
]


async def async_setup(hass: core.HomeAssistant, config: dict):
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass, entry):
    ip = entry.data.get("ip")
    name = entry.data.get("name")
    mac = entry.data.get("mac")

    # 初始 ping
    try:
        delay = await hass.async_add_executor_job(lambda: ping3.ping(ip, timeout=2))
        # ping3 成功返回延迟秒数（浮点数），失败返回 False 或 None
        # 注意：bool 是 int 的子类，必须用 float 而非 (int, float) 排除 bool
        status = "0" if isinstance(delay, float) else "-1"
        _LOGGER.debug("初始 ping -> IP:%s 延迟:%s 状态:%s", ip, delay, status)
    except Exception as e:
        _LOGGER.error("初始 ping 异常 IP:%s err:%s", ip, e)
        status = "-1"

    coordinator = DEVICEDataUpdateCoordinator(hass, entry, ip, name, mac, status)

    await coordinator.async_refresh()
    _LOGGER.debug("初始 refresh 完成 success=%s data=%s",
                  coordinator.last_update_success, coordinator.data)
    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][ip] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def update_listener(hass, entry):
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: core.HomeAssistant, entry: config_entries.ConfigEntry):
    ip = entry.data.get(CONF_IP)
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
    def __init__(self, hass, entry, ip, name, mac, status):
        self.hass = hass
        self.entry = entry
        self.ip = ip
        self.name = name
        self.mac = mac
        self.status = status
        self._isenable = True
        self._last_updated = None

        super().__init__(
            hass,
            _LOGGER,
            name=self.name,
            update_interval=timedelta(seconds=30),
        )

    def set_device_enabled(self, enabled):
        self._isenable = enabled

    async def _async_update_data(self):
        try:
            delay = await self.hass.async_add_executor_job(
                lambda: ping3.ping(self.ip, timeout=2)
            )
            # ping3 成功返回延迟秒数（int/float），失败返回 False 或 None
            # 注意：bool 是 int 的子类，必须用 float 而非 (int, float) 排除 bool
            self.status = "0" if isinstance(delay, float) else "-1"
            _LOGGER.debug("ping3 -> IP:%s 延迟:%s status:%s", self.ip, delay, self.status)
        except Exception as err:
            _LOGGER.error("ping3 异常 IP:%s err:%s", self.ip, err)
            self.status = "-1"
        finally:
            self._last_updated = datetime.now()

        return {
            "ip": self.ip,
            "name": self.name,
            "status": self.status,
        }
