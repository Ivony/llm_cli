import json
import os
from typing import List, Dict, Any


class SessionManager:
    """会话管理器"""
    
    def __init__(self, config, display):
        self.config = config
        self.display = display
        self.current_provider = config.get("general.default_provider", "openai")
        self.history = []
        self.max_history = config.get("general.max_history", 100)
        self.history_file = "session_history.json"
        self.load_history()
    
    def load_history(self):
        """加载历史记录"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except Exception as e:
                self.display.show_error(f"Failed to load history: {e}")
                self.history = []
    
    def save_history(self):
        """保存历史记录"""
        try:
            # 限制历史记录长度
            if len(self.history) > self.max_history:
                self.history = self.history[-self.max_history:]
            
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.display.show_error(f"Failed to save history: {e}")
    
    def add_message(self, role: str, content: str):
        """添加消息到历史记录"""
        self.history.append({"role": role, "content": content})
        self.save_history()
    
    def get_messages(self, limit: int = None) -> List[Dict[str, str]]:
        """获取消息历史"""
        if limit:
            return self.history[-limit:]
        return self.history
    
    def clear_history(self):
        """清空历史记录"""
        self.history = []
        self.save_history()
    
    def set_provider(self, provider_name: str):
        """设置当前模型提供程序"""
        if provider_name in self.config.config.get("providers", {}):
            self.current_provider = provider_name
            self.config.set("general.default_provider", provider_name)
            self.display.show_info(f"Switched to provider: {provider_name}")
        else:
            self.display.show_error(f"Provider {provider_name} not found")
    
    def get_current_provider(self) -> str:
        """获取当前模型提供程序"""
        return self.current_provider
    
    def get_provider_config(self) -> Dict[str, Any]:
        """获取当前提供程序配置"""
        provider_config = self.config.get_provider_config(self.current_provider)
        if provider_config and "endpoint" in provider_config:
            endpoint_identifier = provider_config["endpoint"]
            # 先尝试直接通过endpoint_identifier获取配置
            endpoint_config = self.config.get_endpoint_config(endpoint_identifier)
            # 如果没有找到，尝试通过base_url查找端点
            if not endpoint_config:
                endpoint_key = self.config.get_endpoint_by_base_url(endpoint_identifier)
                if endpoint_key:
                    endpoint_config = self.config.get_endpoint_config(endpoint_key)
            # 合并端点配置到提供程序配置
            if endpoint_config:
                merged_config = provider_config.copy()
                merged_config.update(endpoint_config)
                return merged_config
        return provider_config
