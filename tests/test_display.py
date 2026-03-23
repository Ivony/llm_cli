from unittest.mock import Mock, patch
from ai_cli.display import DisplayManager


def test_display_initialization():
    """测试显示管理器初始化"""
    config = {
        "display": {
            "color_scheme": "auto"
        }
    }
    display = DisplayManager(config)
    assert display.config == config


def test_show_user_input():
    """测试显示用户输入"""
    config = {
        "display": {
            "color_scheme": "auto"
        }
    }
    display = DisplayManager(config)
    
    with patch('builtins.print') as mock_print:
        display.show_user_input("Hello")
        mock_print.assert_called_once()


def test_show_model_output():
    """测试显示模型输出"""
    config = {
        "display": {
            "color_scheme": "auto"
        }
    }
    display = DisplayManager(config)
    
    with patch('builtins.print') as mock_print:
        display.show_model_output("Hi there!")
        mock_print.assert_called_once()


def test_show_error():
    """测试显示错误信息"""
    config = {
        "display": {
            "color_scheme": "auto"
        }
    }
    display = DisplayManager(config)
    
    with patch('builtins.print') as mock_print:
        display.show_error("Error message")
        mock_print.assert_called_once()


def test_show_info():
    """测试显示信息"""
    config = {
        "display": {
            "color_scheme": "auto"
        }
    }
    display = DisplayManager(config)
    
    with patch('builtins.print') as mock_print:
        display.show_info("Info message")
        mock_print.assert_called_once()


def test_show_warning():
    """测试显示警告"""
    config = {
        "display": {
            "color_scheme": "auto"
        }
    }
    display = DisplayManager(config)
    
    with patch('builtins.print') as mock_print:
        display.show_warning("Warning message")
        mock_print.assert_called_once()


def test_clear():
    """测试清屏功能"""
    config = {
        "display": {
            "color_scheme": "auto"
        }
    }
    display = DisplayManager(config)
    
    with patch('os.system') as mock_system:
        display.clear()
        mock_system.assert_called_once()


def test_show_welcome():
    """测试显示欢迎信息"""
    config = {
        "display": {
            "color_scheme": "auto"
        }
    }
    display = DisplayManager(config)
    
    with patch('builtins.print') as mock_print:
        display.show_welcome()
        mock_print.assert_called_once()


def test_show_help():
    """测试显示帮助信息"""
    config = {
        "display": {
            "color_scheme": "auto"
        }
    }
    display = DisplayManager(config)
    
    with patch('builtins.print') as mock_print:
        display.show_help()
        mock_print.assert_called_once()