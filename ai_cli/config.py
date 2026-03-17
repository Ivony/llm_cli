import os
import yaml
from typing import Dict, Any


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        else:
            # 默认配置
            config = {
                "general": {
                    "default_provider": "openai",
                    "max_history": 100,
                    "theme": "default"
                },
                "endpoints": {
                    "openai-standard": {
                        "protocol": "openai",
                        "base_url": "https://api.openai.com/v1"
                    }
                },
                "providers": {
                    "openai": {
                        "endpoint": "openai-standard",
                        "api_key": "",
                        "default_model": "gpt-3.5-turbo",
                        "temperature": 0.7,
                        "max_tokens": 1000
                    }
                },
                "display": {
                    "show_timestamp": True,
                    "color_scheme": "auto",
                    "animation": True
                }
            }
            self.save_config(config)
        
        # 确保配置不为None
        if config is None:
            config = {
                "general": {
                    "default_provider": "openai",
                    "max_history": 100,
                    "theme": "default"
                },
                "endpoints": {
                    "openai-standard": {
                        "protocol": "openai",
                        "base_url": "https://api.openai.com/v1"
                    }
                },
                "providers": {
                    "openai": {
                        "endpoint": "openai-standard",
                        "api_key": "",
                        "default_model": "gpt-3.5-turbo",
                        "temperature": 0.7,
                        "max_tokens": 1000
                    }
                },
                "display": {
                    "show_timestamp": True,
                    "color_scheme": "auto",
                    "animation": True
                }
            }
        
        # 处理环境变量
        self._resolve_env_vars(config)
        return config
    
    def _resolve_env_vars(self, config: Dict[str, Any]):
        """解析环境变量"""
        if config and "providers" in config:
            for provider_name, provider_config in config["providers"].items():
                if "api_key" in provider_config and provider_config["api_key"]:
                    # 检查是否是环境变量名
                    api_key = provider_config["api_key"]
                    if api_key in os.environ:
                        provider_config["api_key"] = os.environ.get(api_key, "")
    
    def save_config(self, config: Dict[str, Any] = None):
        """保存配置文件"""
        if config is None:
            config = self.config
        
        with open(self.config_file, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split(".")
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split(".")
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save_config()
    
    def get_provider_config(self, provider_name: str) -> Dict[str, Any]:
        """获取提供程序配置"""
        return self.config.get("providers", {}).get(provider_name, {})
    
    def get_endpoint_config(self, endpoint_name: str) -> Dict[str, Any]:
        """获取端点配置"""
        return self.config.get("endpoints", {}).get(endpoint_name, {})
    
    def add_endpoint(self, base_url: str, name: str = None, protocol: str = "openai"):
        """添加端点配置"""
        if "endpoints" not in self.config:
            self.config["endpoints"] = {}
        
        # 检查base_url是否已存在
        for endpoint_name, endpoint_config in self.config["endpoints"].items():
            if endpoint_config["base_url"] == base_url:
                raise ValueError(f"Endpoint with base_url '{base_url}' already exists")
        
        # 检查name是否已存在
        if name and name in self.config["endpoints"]:
            raise ValueError(f"Endpoint with name '{name}' already exists")
        
        # 如果没有指定name，使用base_url作为key
        endpoint_key = name if name else base_url
        
        self.config["endpoints"][endpoint_key] = {
            "protocol": protocol,
            "base_url": base_url,
            "name": name  # 保存name以便后续使用
        }
        self.save_config()
    
    def get_endpoint_by_base_url(self, base_url: str) -> str:
        """通过base_url获取端点key"""
        for endpoint_key, endpoint_config in self.config.get("endpoints", {}).items():
            if endpoint_config["base_url"] == base_url:
                return endpoint_key
        return None
    
    def remove_endpoint(self, name: str):
        """移除端点配置"""
        if "endpoints" in self.config and name in self.config["endpoints"]:
            del self.config["endpoints"][name]
            self.save_config()
    
    def add_provider(self, name: str, endpoint: str, api_key: str, **kwargs):
        """添加模型提供程序"""
        if "providers" not in self.config:
            self.config["providers"] = {}
        
        self.config["providers"][name] = {
            "endpoint": endpoint,
            "api_key": api_key,
            **kwargs
        }
        self.save_config()
    
    def remove_provider(self, name: str):
        """移除模型提供程序"""
        if "providers" in self.config and name in self.config["providers"]:
            del self.config["providers"][name]
            self.save_config()
