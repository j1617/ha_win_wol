"""
Hass.io My Custom Switch Plugin Config Flow
"""
import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_IP, CONF_NAME, CONF_MAC

from homeassistant.components.http.view import HomeAssistantView
from aiohttp import web

@config_entries.HANDLERS.register(DOMAIN)
class MyCustomSwitchFlowHandler(config_entries.ConfigFlow):

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL
    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # 检查 IP 是否已存在，防止重复添加
            for entry in self._async_current_entries():
                if entry.data.get(CONF_IP) == user_input.get(CONF_IP):
                    return self.async_abort(reason="already_configured")
            
            # 使用用户输入的名称作为配置条目标题
            return self.async_create_entry(title=user_input.get(CONF_NAME), data=user_input)
        
        
        # 在这里创建一个配置表单页面，让用户填写参数
        return self.async_show_form(
            step_id="user", data_schema=vol.Schema({
                vol.Required("ip", default = ""): str,
                vol.Required("name", default = ""): str,
                vol.Required("mac", default = ""): str,
            })
        )
