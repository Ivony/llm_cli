from ai_cli.adapters import adapter_factory, OpenAIAdapter


def test_adapter_factory():
    """测试适配器工厂"""
    # 测试创建OpenAI适配器
    config = {
        "api_key": "test-key",
        "default_model": "gpt-3.5-turbo"
    }
    adapter = adapter_factory("openai", config)
    assert isinstance(adapter, OpenAIAdapter)


def test_openai_adapter_initialization():
    """测试OpenAI适配器初始化"""
    config = {
        "api_key": "test-key",
        "default_model": "gpt-3.5-turbo",
        "base_url": "http://test-api.com"
    }
    adapter = OpenAIAdapter(config)
    assert adapter.api_key == "test-key"
    assert adapter.model == "gpt-3.5-turbo"
    assert adapter.base_url == "http://test-api.com"


def test_openai_adapter_get_model_info():
    """测试OpenAI适配器获取模型信息"""
    config = {
        "api_key": "test-key",
        "default_model": "gpt-3.5-turbo",
        "base_url": "http://test-api.com"
    }
    adapter = OpenAIAdapter(config)
    model_info = adapter.get_model_info()
    assert model_info["type"] == "openai"
    assert model_info["model"] == "gpt-3.5-turbo"
    assert model_info["base_url"] == "http://test-api.com"
