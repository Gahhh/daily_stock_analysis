# -*- coding: utf-8 -*-
"""
===================================
Discord 平台适配器
===================================

负责：
1. 验证 Discord Interactions 请求
2. 解析 Discord Slash Commands 为统一格式
3. 将响应转换为 Discord 格式
"""

import logging
import json
from typing import Dict, Any, Optional
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

from bot.platforms.base import BotPlatform
from bot.models import BotMessage, WebhookResponse


logger = logging.getLogger(__name__)


class DiscordPlatform(BotPlatform):
    """Discord 平台适配器（支持Slash Commands）"""
    
    def __init__(self, public_key: Optional[str] = None):
        """
        初始化Discord平台适配器
        
        Args:
            public_key: Discord应用的Public Key（用于验证签名）
        """
        self.public_key = public_key
        self._verify_key = None
        
        if public_key:
            try:
                self._verify_key = VerifyKey(bytes.fromhex(public_key))
            except Exception as e:
                logger.warning(f"[Discord] 无法初始化验证密钥: {e}")
    
    @property
    def platform_name(self) -> str:
        """平台标识名称"""
        return "discord"
    
    def verify_request(self, headers: Dict[str, str], body: bytes) -> bool:
        """验证 Discord Interactions 请求签名
        
        Discord 使用 Ed25519 签名验证：
        1. 从请求头获取 X-Signature-Ed25519 和 X-Signature-Timestamp
        2. 使用公钥验证签名
        
        Args:
            headers: HTTP 请求头
            body: 请求体原始字节
            
        Returns:
            签名是否有效
        """
        logger.info("[Discord] 开始验证请求签名")
        
        if not self._verify_key:
            logger.warning("[Discord] 未配置Public Key，跳过签名验证")
            return True
        
        signature = headers.get("x-signature-ed25519") or headers.get("X-Signature-Ed25519")
        timestamp = headers.get("x-signature-timestamp") or headers.get("X-Signature-Timestamp")
        
        logger.info(f"[Discord] 签名头: {signature[:20] if signature else 'None'}...")
        logger.info(f"[Discord] 时间戳头: {timestamp}")
        
        if not signature or not timestamp:
            logger.warning("[Discord] 缺少签名或时间戳")
            return False
        
        try:
            message = timestamp.encode() + body
            self._verify_key.verify(message, bytes.fromhex(signature))
            logger.info("[Discord] Ed25519 签名验证成功 ✓")
            return True
        except BadSignatureError:
            logger.error("[Discord] 签名验证失败：Bad Signature")
            return False
        except Exception as e:
            logger.error(f"[Discord] 签名验证异常: {e}")
            return False
    
    def parse_message(self, data: Dict[str, Any]) -> Optional[BotMessage]:
        """解析 Discord Slash Command 为统一格式
        
        Args:
            data: 解析后的 JSON 数据
            
        Returns:
            BotMessage 对象，或 None（不需要处理）
        """
        # Interaction类型：1=Ping, 2=ApplicationCommand, 3=MessageComponent
        interaction_type = data.get("type")
        
        # Ping请求（验证）直接返回None，在handle_challenge中处理
        if interaction_type == 1:
            return None
        
        # 只处理Application Command (Slash Command)
        if interaction_type != 2:
            return None
        
        # 提取命令信息
        command_data = data.get("data", {})
        command_name = command_data.get("name", "")
        options = command_data.get("options", [])
        
        # 构建命令内容
        content = f"/{command_name}"
        if options:
            # 提取参数值
            args = []
            for option in options:
                args.append(str(option.get("value", "")))
            if args:
                content = f"/{command_name} {' '.join(args)}"
        
        # 提取用户信息
        user = data.get("member", {}).get("user", data.get("user", {}))
        user_id = user.get("id", "")
        user_name = user.get("username", "unknown")
        
        # 提取频道和服务器信息
        channel_id = data.get("channel_id", "")
        guild_id = data.get("guild_id", "")
        
        # 构建 BotMessage 对象
        from bot.models import ChatType
        message = BotMessage(
            platform="discord",
            message_id=data.get("id", ""),
            user_id=user_id,
            user_name=user_name,
            chat_id=channel_id or guild_id,
            chat_type=ChatType.GROUP if guild_id else ChatType.PRIVATE,
            content=content,
            raw_content=content,
            mentioned=False,
            mentions=[],
            raw_data=data
        )
        
        return message
    
    def format_response(self, response: Any, message: BotMessage) -> WebhookResponse:
        """将统一响应转换为 Discord Interaction Response 格式
        
        Args:
            response: 统一响应对象
            message: 原始消息对象
            
        Returns:
            WebhookResponse 对象
        """
        # Discord Interaction Response 格式
        # Type 4 = CHANNEL_MESSAGE_WITH_SOURCE（发送消息）
        discord_response = {
            "type": 4,
            "data": {
                "content": response.text if hasattr(response, "text") else str(response),
                "flags": 0  # 0=普通消息, 64=ephemeral(仅发送者可见)
            }
        }
        
        return WebhookResponse.success(discord_response)
    
    def handle_challenge(self, data: Dict[str, Any]) -> Optional[WebhookResponse]:
        """处理 Discord Ping 验证请求
        
        Discord 在配置 Interactions Endpoint 时会发送 Ping 请求（type=1）
        
        Args:
            data: 请求数据
            
        Returns:
            验证响应，或 None（不是验证请求）
        """
        # Discord Ping 请求的 type 是 1
        if data.get("type") == 1:
            logger.info("[Discord] 收到 Ping 请求，返回 Pong")
            return WebhookResponse.success({
                "type": 1  # Type 1 = PONG
            })
        
        return None

