# 灰字发送插件 (GreyText)

一个用于 AstrBot 的灰字发送插件，仿照 Yunzai-Bot 灰字插件逻辑，通过 NapCat 的扩展 API 发送灰字消息到指定群。

## 功能特点

- 🔤 发送灰字消息到指定 QQ 群
- 🎯 支持自定义消息内容和目标群号
- 📋 提供帮助命令查看使用说明

## 安装方法

1. 将插件目录 `astrbot_plugin_greytext` 放入 AstrBot 的 `data/plugins/` 目录下
2. 重启 AstrBot 或在 WebUI 中重载插件

```bash
cd AstrBot/data/plugins/
git clone <your-plugin-repo> astrbot_plugin_greytext
```

## 使用方法

### 发送灰字消息

```
#hz <内容> <群号>
```

**示例：**
```
#hz 这是一条灰字消息 123456789
```

### 查看帮助

```
hz_help
```

## 注意事项

1. **协议端要求**：需要 NapCat 或支持 `send_packet` API 的 QQ 协议端
2. **权限要求**：机器人需要在目标群中
3. **群号格式**：群号必须是纯数字

## 技术说明

灰字消息是 QQ 的一种特殊消息类型，需要通过原始 PB (Protocol Buffer) 数据包发送。本插件尝试通过以下方式发送：

1. 首先尝试使用 `send_packet` API（NapCat 扩展 API）
2. 如果不可用，尝试 `_send_packet` 等备选 API
3. 如果都不支持，回退到发送普通消息

## 兼容性

- AstrBot 版本：>= 4.0.0
- 协议端：NapCat（推荐）、或其他支持 `send_packet` API 的 OneBot V11 实现

## 更新日志

### v1.0.0
- 初始版本
- 实现基本的灰字发送功能
- 添加帮助命令

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！