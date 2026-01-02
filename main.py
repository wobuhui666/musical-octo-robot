"""
灰字发送插件 for AstrBot

仿照 Yunzai-Bot 灰字插件逻辑，通过 NapCat 的扩展 API 发送灰字消息到指定群。

使用方法：
    #hz 内容 群号
    
例如：
    #hz 这是一条灰字消息 123456789
"""

import re

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register

# 尝试导入 aiocqhttp 相关模块
try:
    from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import (
        AiocqhttpMessageEvent,
    )
    from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_platform_adapter import (
        AiocqhttpAdapter,
    )

    AIOCQHTTP_AVAILABLE = True
except ImportError:
    AIOCQHTTP_AVAILABLE = False
    logger.warning("aiocqhttp 模块不可用，灰字发送功能将无法使用")


@register("greytext", "AstrBot Plugin Developer", "灰字发送插件 - 发送灰字消息到指定群", "1.0.0")
class GreyTextPlugin(Star):
    """灰字发送插件"""

    def __init__(self, context: Context, config: dict | None = None):
        super().__init__(context, config)
        self.context = context

    @filter.regex(r"^#hz\s+(.+?)\s+(\d+)$")
    async def send_grey(self, event: AstrMessageEvent):
        """
        发送灰字消息到指定群

        命令格式: #hz 内容 群号
        """
        if not AIOCQHTTP_AVAILABLE:
            yield event.plain_result("错误：aiocqhttp 模块不可用，无法发送灰字消息")
            return

        # 从事件中获取消息字符串并手动进行正则匹配
        msg = event.message_str
        pattern = re.compile(r"^#hz\s+(.+?)\s+(\d+)$")
        match = pattern.match(msg)
        
        if not match:
            yield event.plain_result("命令格式错误，请使用: #hz <内容> <群号>")
            return

        # 提取正则匹配的内容和群号
        content = match.group(1)
        group_id = int(match.group(2))

        logger.info(f"准备发送灰字消息到群 {group_id}，内容: {content}")

        # 获取 bot 实例
        bot = None

        # 方法1: 如果当前事件是 AiocqhttpMessageEvent，直接获取 bot
        if isinstance(event, AiocqhttpMessageEvent):
            bot = event.bot
        else:
            # 方法2: 从平台管理器获取 aiocqhttp 适配器
            try:
                platforms = self.context.platform_manager.get_insts()
                for platform in platforms:
                    if isinstance(platform, AiocqhttpAdapter):
                        bot = platform.get_client()
                        break
            except Exception as e:
                logger.error(f"获取 aiocqhttp 适配器失败: {e}")

        if not bot:
            yield event.plain_result("错误：无法获取 QQ 协议端连接")
            return

        # 构造灰字消息的 PB 数据包
        # 这个结构来自原始 Yunzai-Bot 插件
        packet = {
            "25": {
                "1": {
                    "1": 11,
                    "50": "3573715425",
                    "20": {
                        "2": 3573715425,
                        "3": 3009074854,
                        "4": 800800864,
                    },
                    "5": 8,
                    "0": {"1": 1},
                    "28": {
                        "1": 2,
                        "2": content,  # 灰字内容
                        "3": 800800864,
                        "4": {"1": "", "2": 0},
                    },
                    "30": 2,
                    "14": 1,
                }
            }
        }

        try:
            # 尝试通过 NapCat 的扩展 API 发送原始数据包
            # NapCat 支持 send_packet 扩展 API
            result = await bot.call_action(
                action="send_packet",
                params={
                    "group_id": group_id,
                    "packet": packet,
                },
            )
            logger.info(f"灰字消息发送结果: {result}")
            yield event.plain_result(f"灰字消息已发送到群 {group_id}")

        except Exception as e:
            error_msg = str(e)
            logger.error(f"发送灰字消息失败: {error_msg}")

            # 如果 send_packet 不可用，尝试其他方法
            if "not found" in error_msg.lower() or "不支持" in error_msg:
                # 尝试使用 _send_packet 或其他可能的 API 名称
                alternative_actions = [
                    "_send_packet",
                    "send_forward_msg",  # 尝试合并转发作为备选
                ]

                for action in alternative_actions:
                    try:
                        if action == "send_forward_msg":
                            # 作为备选，发送普通消息
                            await bot.call_action(
                                action="send_group_msg",
                                group_id=group_id,
                                message=[{"type": "text", "data": {"text": f"[灰字] {content}"}}],
                            )
                            yield event.plain_result(
                                f"注意：send_packet API 不可用，已发送普通消息到群 {group_id}"
                            )
                            return
                        else:
                            result = await bot.call_action(
                                action=action,
                                params={
                                    "group_id": group_id,
                                    "packet": packet,
                                },
                            )
                            logger.info(f"使用 {action} 发送成功: {result}")
                            yield event.plain_result(f"灰字消息已发送到群 {group_id}")
                            return
                    except Exception:
                        continue

                yield event.plain_result(
                    f"发送失败：你的 QQ 协议端不支持 send_packet API。\n"
                    f"灰字功能需要 NapCat 或支持原始数据包发送的协议端。\n"
                    f"错误详情: {error_msg}"
                )
            else:
                yield event.plain_result(f"发送灰字消息失败: {error_msg}")

    @filter.command("hz_help")
    async def grey_help(self, event: AstrMessageEvent):
        """显示灰字发送帮助信息"""
        help_text = """【灰字发送插件帮助】

📝 命令格式：
   #hz <内容> <群号>

📋 示例：
   #hz 这是一条灰字消息 123456789

⚠️ 注意事项：
1. 需要 NapCat 或支持 send_packet API 的 QQ 协议端
2. 群号必须是纯数字
3. 机器人需要在目标群中

🔧 如果发送失败：
- 检查协议端是否支持 send_packet API
- 检查机器人是否在目标群中
- 检查群号是否正确"""

        yield event.plain_result(help_text)

    async def terminate(self):
        """插件停用时调用"""
        logger.info("灰字发送插件已停用")