# AstrBot 插件开发详尽指南（中文）

> 本文基于 AstrBot 官方文档整理，包含快速上手、示例代码、插件配置与发布流程的汇总。适用于想要在 AstrBot 上开发、测试并发布插件（Star）的开发者。

---

## 目录
1. 简介与原则 ✅
2. 环境准备与模板 🔧
3. 最小示例（main.py）🧩
4. 事件监听与命令（指令、参数、分组、优先级等）📨
5. 发送消息与控制传播 ↔️
6. 插件配置（metadata、_conf_schema.json、AstrBotConfig）⚙️
7. 依赖管理与编码规范（requirements、ruff、异步库）📦
8. 文转图、AI 工具与会话管理（FunctionTool、ConversationManager）🤖
9. 存储 / 数据持久化（data 目录）💾
10. 调试、热重载与测试 🧪
11. 打包/发布与市场（注意）📤
12. 检查清单 (QuickStart) ✅

---

## 1) 简介与开发原则 ✅
- 插件（Star）基于 Python，必须继承 `Star` 基类并使用 `@register` 装饰器注册。
- 开发原则：
  - 功能需经过测试、包含注释、错误处理健壮；
  - 持久化数据应存储在 AstrBot 的 `data` 目录下（避免更新/重装时数据被覆盖）；
  - 在提交前使用 `ruff` 格式化代码；
  - 避免使用同步网络库 `requests`（优先使用 `aiohttp` 或 `httpx`）。

---

## 2) 环境准备与模板 🔧
- 获取官方模板：`helloworld`（GitHub 模板）。建议仓库名以 `astrbot_plugin_` 开头。
- 本地开发：
```bash
git clone https://github.com/AstrBotDevs/AstrBot
mkdir -p AstrBot/data/plugins
cd AstrBot/data/plugins
git clone <your-plugin-repo>
```
- 修改 `metadata.yaml`，添加 `display_name`、`author`、`version`、`repo` 等信息。
- 可选：在插件目录放 `logo.png`（建议 256x256，1:1）用于市场展示。

---

## 3) 最小示例（main.py）🧩
- 插件文件名约定为 `main.py`。
- 示例：
```py
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

@register("helloworld", "you", "A simple Hello World plugin", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.command("helloworld")
    async def helloworld(self, event: AstrMessageEvent):
        '''这是 hello world 指令'''
        user_name = event.get_sender_name()
        logger.info("触发 hello world 指令")
        yield event.plain_result(f"Hello, {user_name}!")
```
- 可实现 `terminate(self)`，在插件停用/卸载时被调用。

---

## 4) 事件监听与命令 📨
- 导入：`from astrbot.api.event import filter, AstrMessageEvent`
- 注册指令：`@filter.command("name")`
- 自动参数解析：
```py
@filter.command("add")
def add(self, event: AstrMessageEvent, a: int, b: int):
    yield event.plain_result(f"结果是: {a + b}")
```
- 指令组示例：
```py
@filter.command_group("math")
def math(self): pass

@math.command("add")
async def add(self, event: AstrMessageEvent, a:int, b:int):
    yield event.plain_result(f"{a+b}")
```
- 支持事件类型、私聊/群聊过滤、平台过滤、管理员指令及优先级控制（详见官方文档）。

---

## 5) 发送消息与控制事件传播 ↔️
- 发送纯文本：`yield event.plain_result("文本")`。
- 还有更丰富的 `MessageEventResult` 类型可用以实现卡片、图片等（参见 docs）。
- 可以控制事件是否继续传播以及处理优先级。

---

## 6) 插件配置与 Schema ⚙️
- `metadata.yaml`：必填基本元信息；可设置 `display_name` 等。
- `_conf_schema.json`：用于定义插件配置的 Schema（支持 `string`, `int`, `float`, `bool`, `object`, `list`, `text` 等类型），支持 `hint`, `editor_mode`, `_special`（供 WebUI 使用）。
- 在插件中读取配置：
```py
@register("config", "author", "配置示例", "1.0.0")
class ConfigPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        # self.config.save_config()
```

---

## 7) 依赖管理与编码规范 📦
- 在插件目录创建 `requirements.txt` 并列出第三方依赖（AstrBot 安装插件时会读取）。
- 使用 `ruff` 进行格式化和静态检查。
- 避免使用阻塞 IO（如 `requests`）；使用 `aiohttp`、`httpx` 等异步库。
- 日志：使用 `from astrbot.api import logger`。

---

## 8) 文转图、AI 工具与会话管理 🤖
- 文转图（HTML -> 图像）：支持自定义 HTML、动画、缩放参数（`animations`, `caret`, `scale` 等）。
- AI：通过 AstrBot 的 provider 调用 LLM；推荐把函数工具实现为类并放置于 `tools/` 目录，继承 `FunctionTool`。
- FunctionTool 示例（片段）：
```py
from astrbot.api import FunctionTool
from dataclasses import dataclass, field

@dataclass
class HelloWorldTool(FunctionTool):
    name: str = "hello_world"
    description: str = "Say hello"
    parameters: dict = field(default_factory=lambda: {...})
    async def call(self, **kwargs):
        return {"result": "hello"}
```
- ConversationManager 提供对话管理能力（`new_conversation`, `get_human_readable_context` 等）。

---

## 9) 存储 / 数据持久化 💾
- 持久化数据应写入 AstrBot 的 `data` 目录而不是插件目录，避免更新覆盖。
- 可以使用 AstrBot 提供的存储 API，或在 `data/` 下管理文件/DB。

---

## 10) 调试、热重载与测试 🧪
- 启动 AstrBot 本体以调试插件；支持 WebUI 的 Hot Reload（插件管理 -> 重载插件）。
- 推荐编写单元测试并进行手动流程测试，确保异常被捕获且不会使插件崩溃。
- 可在 `__init__` 中注册异步任务：
```py
import asyncio
asyncio.create_task(self.my_task())
```

---

## 11) 打包/发布与市场 📤
- 准备 `metadata.yaml`, `README`, `logo.png`, `requirements.txt`, `_conf_schema.json`。
- 发布到 GitHub；如需提交到插件市场，请补充文档、演示与截图并遵循项目的发布流程。

---

## 12) 检查清单 (QuickStart) ✅
- [ ] 使用模板创建仓库（`astrbot_plugin_<name>`）
- [ ] 添加 `main.py`, `metadata.yaml`, `requirements.txt`
- [ ] 可选：添加 `logo.png`（256x256）
- [ ] 将仓库 clone 到 `AstrBot/data/plugins/`，启动 AstrBot 并测试指令
- [ ] 在 WebUI 中使用重载功能测试热重载与配置界面
- [ ] 编写 README、示例与测试，提交 PR

---

## 常见注意事项与最佳实践 🔍
- 使用异步网络库并对外部请求设置超时与错误处理；
- 将可配置项通过 `_conf_schema.json` 暴露以便 WebUI 编辑；
- 控制 LLM 调用的 token 与并发，避免高额费用与性能问题；
- 代码提交前运行 `ruff`、编写测试并在本地/CI 上验证。

---

如果需要，我可以继续：
- 在仓库中创建一个示例插件（`data/plugins/astrbot_plugin_example`）并提交为后续 PR；
- 或将此文档拆分成 `QuickStart` 与 `Reference` 两份文件并提交。

---

*生成于 AstrBot 官方文档的整理汇总。若需引用或扩展某一节的完整示例，我可以继续补全并提交到仓库。*
