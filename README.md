# ha_win_wol

HA插件交流QQ群： 754364399

关注公众号【工具箱达人】，里面有详细的使用教程

## 版本历史

### v3.1.1 (2026-05-28)
- 修复 `binary_sensor.py` 中 docstring 引号错误（弯引号导致 SyntaxError）
- 修复 `extra_state_attributes` 中 `last_updated` 属性名错误（应为 `_last_updated`）

### v3.1.0 (2026-05-28)
- 修复 `extra_state_attributes` 中 `last_updated` 属性名错误（应为 `_last_updated`）
- 在 `DEVICEDataUpdateCoordinator` 中维护 `_last_updated` 时间戳

### v3.0.1 (2026-05-28)
- 修复 binary_sensor 平台加载失败问题
- `device_class` 改用 `BinarySensorDeviceClass.CONNECTIVITY` 枚举
- `async_setup_entry` 增加 coordinator 空值检查
- 移除冗余的 `async_added_to_hass` 重写

### v3.0.0 (2026-05-28)
- 新增状态实体（binary_sensor）：通过ping检测电脑开关机状态
- 状态实体与开关实体共享同一设备
- 状态更新间隔优化为30秒
- coordinator增加实时ping检测功能

---

#### 介绍
ha插件，win10/11电脑网络唤醒ha插件

#### 功能特性

1. **远程唤醒**：通过发送Magic Packet唤醒局域网内的电脑
2. **状态监控**：实时显示电脑开关机状态（通过ping检测）
3. **设备管理**：支持添加多台电脑，每台电脑显示为一个设备

#### 使用说明

1. 手动下载自定义插件的代码，并将其解压缩到 Home Assistant 配置目录的 "custom_components" 文件夹中。请注意，如果 "custom_components" 文件夹不存在，则需要手动创建它。

2. 例如，如果您要安装的插件名为 "ha_win_wol"，则您应该将其解压缩到以下路径：<config directory>/custom_components/ha_win_wol/。

3. <config directory> 是 Home Assistant 的配置文件夹目录，通常在您安装 Home Assistant 的设备上。您可以在 Home Assistant 的 Web 界面中的 "Configuration"（配置）> "General"（常规）选项卡中找到该目录。

4. 重新启动 Home Assistant，以使新插件加载和生效。

5. 打开 Home Assistant 的 Web 界面，导航到 "Configuration"（配置）> "Integrations"（集成）页面中，然后单击 "Add Integration"（添加集成）按钮。

6. 在弹出窗口中选择您要安装的插件，并按照提示进行设置。


