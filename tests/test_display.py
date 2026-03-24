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


def test_aichatapp_update_assistant_message():
    """测试AIChatApp助手消息流式更新（验证call_later/set_timer参数传递修复）
    
    回归测试：修复"the first argument must be callable"错误
    
    问题场景：
    在流式输出时，update_assistant_message 使用 set_timer 进行批量UI更新。
    Textual 的 call_later 方法签名是 call_later(callback) 没有时间参数，
    错误地使用 call_later(delay, callback) 形式会导致 "the first argument must be callable" 错误。
    
    验证点：
    1. update_assistant_message 方法正确使用 set_timer
    2. _latest_content 属性被正确设置
    3. _do_update_message 正确执行消息更新
    """
    from ai_cli.display import AIChatApp
    from unittest.mock import MagicMock, patch, AsyncMock
    
    # 创建模拟的CLI实例
    mock_cli = MagicMock()
    
    with patch.object(AIChatApp, 'run') as mock_run:
        app = AIChatApp(cli=mock_cli)
        
        # 模拟流式消息状态
        app.is_streaming = True
        app.current_stream_message = MagicMock()
        app.current_stream_message.update_content = MagicMock()
        
        # 模拟DOM查询返回
        mock_container = MagicMock()
        mock_container.scroll_end = MagicMock()
        
        # Mock set_timer 以避免需要事件循环
        with patch.object(app, 'set_timer') as mock_set_timer, \
             patch.object(app, 'query_one') as mock_query:
            
            mock_query.return_value = mock_container
            
            # 第一次调用更新
            app.update_assistant_message("Hello")
            
            # 验证最新内容已保存
            assert hasattr(app, '_latest_content')
            assert app._latest_content == "Hello"
            
            # 验证set_timer被正确调用（参数顺序：delay, callback）
            mock_set_timer.assert_called_once()
            args = mock_set_timer.call_args
            assert args[0][0] == 0.016  # 延迟时间
            assert callable(args[0][1])  # 回调函数是可调用的
            
            # 第二次调用更新（模拟快速流式输出）
            mock_set_timer.reset_mock()
            app.update_assistant_message("Hello World")
            
            # 验证内容已更新
            assert app._latest_content == "Hello World"
            
            # 验证_scheduled标志已设置
            assert app._update_scheduled == True
            
        # 模拟执行实际更新操作
        with patch.object(app, 'query_one') as mock_query:
            mock_query.return_value = mock_container
            app._do_update_message()
        
        # 验证_scheduled标志被重置
        assert app._update_scheduled == False
        
        # 验证update_content被调用
        app.current_stream_message.update_content.assert_called_with("Hello World")