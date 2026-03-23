"""
大模型对话管理模块 - 封装与大模型交互、对话管理、消息处理的核心逻辑
"""
import asyncio
from typing import Optional, Dict, List, Any, AsyncGenerator, Callable
from dataclasses import dataclass


@dataclass
class ChatMessage:
    """聊天消息"""
    role: str  # "user", "assistant", "system"
    content: str


@dataclass
class ChatResult:
    """对话结果"""
    success: bool
    content: str = ""
    error: str = ""
    provider_name: str = ""


class ModelChatManager:
    """
    大模型对话管理器
    封装：适配器创建、消息历史管理、流式响应处理
    """
    
    def __init__(self, cli: Any):
        self.cli = cli  # CLI实例引用
    
    def get_provider_config(self) -> Dict[str, Any]:
        """获取当前提供程序配置"""
        return self.cli.session.get_provider_config()
    
    def get_messages(self) -> List[Dict[str, str]]:
        """获取当前会话消息历史"""
        return self.cli.session.get_messages()
    
    def get_current_provider_name(self) -> str:
        """获取当前提供程序名称"""
        return self.cli.session.get_current_provider()
    
    def add_user_message(self, content: str) -> None:
        """添加用户消息到会话历史"""
        self.cli.session.add_message("user", content)
    
    def add_assistant_message(self, content: str) -> None:
        """添加助手消息到会话历史"""
        self.cli.session.add_message("assistant", content)
    
    def create_adapter(self) -> Any:
        """
        创建大模型适配器
        返回适配器实例，失败则抛出异常
        """
        provider_config = self.get_provider_config()
        
        if not provider_config.get("api_key"):
            raise ValueError("API key not set for current provider")
        
        return self.cli.adapter_factory(
            provider_config["protocol"],
            provider_config
        )
    
    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        on_chunk: Optional[Callable[[str], None]] = None
    ) -> ChatResult:
        """
        流式对话
        :param messages: 消息历史列表
        :param on_chunk: 每收到一个chunk时的回调函数
        :return: 对话结果
        """
        full_response = ""
        provider_name = self.get_current_provider_name()
        
        try:
            adapter = self.create_adapter()
            
            try:
                if hasattr(adapter, 'chat_stream_async'):
                    # 支持异步流式接口（httpx版本）
                    async for chunk in adapter.chat_stream_async(messages):
                        full_response += chunk
                        if on_chunk:
                            on_chunk(full_response)
                        # 给UI刷新的机会
                        await asyncio.sleep(0)
                else:
                    # 兼容同步接口（回退方案）
                    for chunk in adapter.chat_stream(messages):
                        full_response += chunk
                        if on_chunk:
                            on_chunk(full_response)
                        await asyncio.sleep(0)
            finally:
                # 关闭httpx客户端（如果适配器支持）
                if hasattr(adapter, 'close'):
                    if asyncio.iscoroutinefunction(adapter.close):
                        await adapter.close()
                    else:
                        adapter.close()
            
            return ChatResult(
                success=True,
                content=full_response,
                provider_name=provider_name
            )
            
        except Exception as e:
            return ChatResult(
                success=False,
                error=str(e),
                provider_name=provider_name
            )
    
    async def send_message(
        self,
        user_input: str,
        on_chunk: Optional[Callable[[str], None]] = None
    ) -> ChatResult:
        """
        发送用户消息并获取响应
        :param user_input: 用户输入文本
        :param on_chunk: 每收到一个chunk时的回调函数
        :return: 对话结果
        """
        # 添加用户消息到历史
        self.add_user_message(user_input)
        
        # 获取消息历史
        messages = self.get_messages()
        
        # 调用大模型
        result = await self.stream_chat(messages, on_chunk)
        
        # 如果成功，添加助手响应到历史
        if result.success and result.content:
            self.add_assistant_message(result.content)
        
        return result


class ChatSession:
    """
    会话状态管理
    （可用于扩展多会话支持）
    """
    
    def __init__(self, session_id: str = "default"):
        self.session_id = session_id
        self.messages: List[ChatMessage] = []
        self.is_active: bool = True
    
    def add_message(self, role: str, content: str) -> None:
        """添加消息"""
        self.messages.append(ChatMessage(role=role, content=content))
    
    def get_messages(self) -> List[ChatMessage]:
        """获取所有消息"""
        return self.messages.copy()
    
    def clear(self) -> None:
        """清空会话"""
        self.messages.clear()
    
    def to_dict_list(self) -> List[Dict[str, str]]:
        """转换为字典列表（适配大模型API格式）"""
        return [{"role": msg.role, "content": msg.content} for msg in self.messages]


# 工具函数
def format_messages_for_api(messages: List[ChatMessage]) -> List[Dict[str, str]]:
    """将内部消息格式转换为大模型API期望的格式"""
    return [{"role": msg.role, "content": msg.content} for msg in messages]