import httpx
import json
from typing import Dict, List, Any, Generator, AsyncGenerator
from .base import ModelAdapter


class OpenAIAdapter(ModelAdapter):
    """OpenAI模型适配器 - 使用httpx异步客户端"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.model = config.get("default_model", "gpt-3.5-turbo")
        self.base_url = config.get("base_url", "https://api.openai.com/v1")
        # 创建httpx异步客户端
        timeout = config.get("timeout", 300)
        self.client = httpx.AsyncClient(
            timeout=timeout,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
    
    def generate(self, prompt: str, **kwargs) -> str:
        """生成模型响应（同步兼容）"""
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, **kwargs)
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """进行对话（非流式，同步兼容）"""
        import asyncio
        return asyncio.run(self.chat_async(messages, **kwargs))
    
    async def chat_async(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """进行对话（异步，非流式）"""
        url = f"{self.base_url}/chat/completions"
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.get("temperature", 0.7)),
            "max_tokens": kwargs.get("max_tokens", self.config.get("max_tokens", 1000))
        }
        
        response = await self.client.post(url, json=data)
        response.raise_for_status()
        
        return response.json()["choices"][0]["message"]["content"]
    
    def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> Generator[str, None, None]:
        """进行对话（流式，同步兼容）"""
        import asyncio
        
        async def consume_async_generator():
            items = []
            async for chunk in self.chat_stream_async(messages, **kwargs):
                items.append(chunk)
            return items
        
        chunks = asyncio.run(consume_async_generator())
        for chunk in chunks:
            yield chunk
    
    async def chat_stream_async(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """进行对话（流式异步）"""
        url = f"{self.base_url}/chat/completions"
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.get("temperature", 0.7)),
            "max_tokens": kwargs.get("max_tokens", self.config.get("max_tokens", 1000)),
            "stream": True
        }
        
        async with self.client.stream("POST", url, json=data) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    if line.startswith('data: '):
                        line = line[6:]
                        if line == '[DONE]':
                            break
                        try:
                            data = json.loads(line)
                            content = data.get('choices', [{}])[0].get('delta', {}).get('content')
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            pass
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "type": "openai",
            "model": self.model,
            "base_url": self.base_url
        }
    
    async def close(self):
        """关闭httpx客户端"""
        await self.client.aclose()