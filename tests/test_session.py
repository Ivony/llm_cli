import os
import tempfile
from ai_cli.config import ConfigManager
from ai_cli.display import DisplayManager
from ai_cli.session import SessionManager


def test_session_initialization():
    """测试会话管理器初始化"""
    # 清理历史记录文件
    if os.path.exists("session_history.json"):
        os.unlink("session_history.json")
    
    # 创建临时配置文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_config = f.name
    
    try:
        config = ConfigManager(temp_config)
        display = DisplayManager(config)
        session = SessionManager(config, display)
        
        assert session.current_provider == config.get("general.default_provider")
        assert session.max_history == config.get("general.max_history")
        assert len(session.history) == 0
    finally:
        os.unlink(temp_config)
        # 清理历史记录文件
        if os.path.exists("session_history.json"):
            os.unlink("session_history.json")


def test_message_management():
    """测试消息管理功能"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_config = f.name
    
    try:
        config = ConfigManager(temp_config)
        display = DisplayManager(config)
        session = SessionManager(config, display)
        
        # 添加消息
        session.add_message("user", "Hello")
        session.add_message("assistant", "Hi there!")
        
        # 检查消息是否添加成功
        history = session.get_messages()
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello"
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == "Hi there!"
        
        # 测试历史记录限制
        session.max_history = 1
        session.add_message("user", "Another message")
        history = session.get_messages()
        assert len(history) == 1
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Another message"
        
        # 清空历史记录
        session.clear_history()
        assert len(session.get_messages()) == 0
    finally:
        os.unlink(temp_config)
        if os.path.exists("session_history.json"):
            os.unlink("session_history.json")


def test_provider_management():
    """测试提供程序管理功能"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_config = f.name
    
    try:
        config = ConfigManager(temp_config)
        # 添加测试提供程序
        config.add_provider(
            name="test-provider",
            endpoint="openai-standard",
            api_key="test-key"
        )
        
        display = DisplayManager(config)
        session = SessionManager(config, display)
        
        # 切换提供程序
        session.set_provider("test-provider")
        assert session.current_provider == "test-provider"
        
        # 检查提供程序配置
        provider_config = session.get_provider_config()
        assert provider_config["endpoint"] == "openai-standard"
        assert provider_config["api_key"] == "test-key"
        assert provider_config["protocol"] == "openai"
    finally:
        os.unlink(temp_config)
        if os.path.exists("session_history.json"):
            os.unlink("session_history.json")
