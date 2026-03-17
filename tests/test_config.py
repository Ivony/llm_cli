import os
import tempfile
import yaml
from ai_cli.config import ConfigManager


def test_config_loading():
    """测试配置加载功能"""
    # 创建临时配置文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({
            "general": {
                "default_provider": "test"
            },
            "providers": {
                "test": {
                    "api_format": "openai",
                    "api_key": "test-key"
                }
            }
        }, f)
        temp_config = f.name
    
    try:
        # 加载配置
        config = ConfigManager(temp_config)
        assert config.get("general.default_provider") == "test"
        assert config.get_provider_config("test")["api_key"] == "test-key"
    finally:
        # 清理临时文件
        os.unlink(temp_config)


def test_config_saving():
    """测试配置保存功能"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_config = f.name
    
    try:
        # 创建配置管理器
        config = ConfigManager(temp_config)
        
        # 修改配置
        config.set("general.default_provider", "new-test")
        
        # 重新加载配置
        new_config = ConfigManager(temp_config)
        assert new_config.get("general.default_provider") == "new-test"
    finally:
        os.unlink(temp_config)


def test_provider_management():
    """测试提供程序管理功能"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_config = f.name
    
    try:
        config = ConfigManager(temp_config)
        
        # 添加提供程序
        config.add_provider(
            name="test-provider",
            endpoint="openai-standard",
            api_key="test-key",
            default_model="test-model"
        )
        
        # 检查提供程序是否添加成功
        provider_config = config.get_provider_config("test-provider")
        assert provider_config["endpoint"] == "openai-standard"
        assert provider_config["api_key"] == "test-key"
        assert provider_config["default_model"] == "test-model"
        
        # 移除提供程序
        config.remove_provider("test-provider")
        assert "test-provider" not in config.config.get("providers", {})
    finally:
        os.unlink(temp_config)


def test_env_var_resolution():
    """测试环境变量解析功能"""
    # 设置环境变量
    os.environ["TEST_API_KEY"] = "env-test-key"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({
            "providers": {
                "test": {
                    "api_format": "openai",
                    "api_key": "TEST_API_KEY"
                }
            }
        }, f)
        temp_config = f.name
    
    try:
        config = ConfigManager(temp_config)
        assert config.get_provider_config("test")["api_key"] == "env-test-key"
    finally:
        os.unlink(temp_config)
        # 清理环境变量
        if "TEST_API_KEY" in os.environ:
            del os.environ["TEST_API_KEY"]
