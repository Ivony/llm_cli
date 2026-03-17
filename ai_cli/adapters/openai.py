import requests
from typing import Dict, List, Any
from .base import ModelAdapter


class OpenAIAdapter(ModelAdapter):
    """OpenAI模型适配器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.model = config.get("default_model", "gpt-3.5-turbo")
        self.base_url = config.get("base_url", "https://api.openai.com/v1")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """生成模型响应"""
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, **kwargs)
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """进行对话"""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.get("temperature", 0.7)),
            "max_tokens": kwargs.get("max_tokens", self.config.get("max_tokens", 1000))
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        return response.json()["choices"][0]["message"]["content"]
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "type": "openai",
            "model": self.model,
            "base_url": self.base_url
        }
