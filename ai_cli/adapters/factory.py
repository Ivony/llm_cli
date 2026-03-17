from typing import Dict, Any
from .openai import OpenAIAdapter


def adapter_factory(protocol: str, config: Dict[str, Any]) -> Any:
    """根据协议创建适配器实例"""
    adapters = {
        "openai": OpenAIAdapter
    }
    
    if protocol not in adapters:
        raise ValueError(f"Unsupported protocol: {protocol}")
    
    return adapters[protocol](config)
