from unittest.mock import Mock, patch, MagicMock
from ai_cli.cli import AICLI


@patch('ai_cli.cli.PromptSession')
def test_cli_initialization(mock_prompt_session):
    """测试CLI初始化"""
    # 模拟PromptSession
    mock_prompt_session.return_value = MagicMock()
    
    # 模拟控制台输出
    with patch('ai_cli.display.Console') as mock_console:
        mock_console.return_value = MagicMock()
        
        cli = AICLI()
        assert cli.config is not None
        assert cli.display is not None
        assert cli.session is not None
        assert cli.prompt_session is not None


@patch('ai_cli.cli.PromptSession')
def test_handle_command_help(mock_prompt_session):
    """测试处理help命令"""
    mock_prompt_session.return_value = MagicMock()
    
    with patch('ai_cli.display.Console') as mock_console:
        mock_console.return_value = MagicMock()
        
        cli = AICLI()
        
        with patch.object(cli.display, 'show_help') as mock_show_help:
            cli._handle_command("/help")
            mock_show_help.assert_called_once()


@patch('ai_cli.cli.PromptSession')
def test_handle_command_exit(mock_prompt_session):
    """测试处理exit命令"""
    mock_prompt_session.return_value = MagicMock()
    
    with patch('ai_cli.display.Console') as mock_console:
        mock_console.return_value = MagicMock()
        
        cli = AICLI()
        
        with patch('sys.exit') as mock_exit:
            cli._handle_command("/exit")
            mock_exit.assert_called_once_with(0)


@patch('ai_cli.cli.PromptSession')
def test_handle_command_clear(mock_prompt_session):
    """测试处理clear命令"""
    mock_prompt_session.return_value = MagicMock()
    
    with patch('ai_cli.display.Console') as mock_console:
        mock_console.return_value = MagicMock()
        
        cli = AICLI()
        
        with patch.object(cli.display, 'clear') as mock_clear:
            cli._handle_command("/clear")
            mock_clear.assert_called_once()


@patch('ai_cli.cli.PromptSession')
def test_handle_command_history(mock_prompt_session):
    """测试处理history命令"""
    mock_prompt_session.return_value = MagicMock()
    
    with patch('ai_cli.display.Console') as mock_console:
        mock_console.return_value = MagicMock()
        
        cli = AICLI()
        
        with patch.object(cli, '_show_history') as mock_show_history:
            cli._handle_command("/history")
            mock_show_history.assert_called_once()


@patch('ai_cli.cli.PromptSession')
def test_handle_command_config(mock_prompt_session):
    """测试处理config命令"""
    mock_prompt_session.return_value = MagicMock()
    
    with patch('ai_cli.display.Console') as mock_console:
        mock_console.return_value = MagicMock()
        
        cli = AICLI()
        
        with patch.object(cli, '_show_config') as mock_show_config:
            cli._handle_command("/config")
            mock_show_config.assert_called_once()


@patch('ai_cli.cli.PromptSession')
def test_handle_model_command_list(mock_prompt_session):
    """测试处理model list命令"""
    mock_prompt_session.return_value = MagicMock()

    with patch('ai_cli.display.Console') as mock_console:
        mock_console.return_value = MagicMock()

        cli = AICLI()

        with patch.object(cli.model_command, '_list_providers') as mock_list_providers, \
             patch.object(cli.model_command, '_list_endpoints') as mock_list_endpoints:
            cli.model_command.handle(["list"])
            mock_list_endpoints.assert_called_once()
            mock_list_providers.assert_called_once()

@patch('ai_cli.cli.PromptSession')
def test_handle_model_command_add_provider(mock_prompt_session):
    """测试处理model add provider命令"""
    mock_prompt_session.return_value = MagicMock()

    with patch('ai_cli.display.Console') as mock_console:
        mock_console.return_value = MagicMock()

        cli = AICLI()

        with patch.object(cli.model_command, '_add_provider') as mock_add_provider:
            cli.model_command.handle(["add", "provider", "test", "openai", "test-key", "test-model"])
            mock_add_provider.assert_called_once_with(["test", "openai", "test-key", "test-model"])

@patch('ai_cli.cli.PromptSession')
def test_handle_model_command_remove_provider(mock_prompt_session):
    """测试处理model remove provider命令"""
    mock_prompt_session.return_value = MagicMock()

    with patch('ai_cli.display.Console') as mock_console:
        mock_console.return_value = MagicMock()

        cli = AICLI()

        with patch.object(cli.model_command, '_remove_provider') as mock_remove_provider:
            cli.model_command.handle(["remove", "provider", "test"])
            mock_remove_provider.assert_called_once_with("test")

@patch('ai_cli.cli.PromptSession')
def test_handle_model_command_set_provider(mock_prompt_session):
    """测试处理model set provider命令"""
    mock_prompt_session.return_value = MagicMock()

    with patch('ai_cli.display.Console') as mock_console:
        mock_console.return_value = MagicMock()

        cli = AICLI()

        with patch.object(cli.session, 'set_provider') as mock_set_provider:
            cli.model_command.handle(["set", "provider", "test"])
            mock_set_provider.assert_called_once_with("test")


@patch('ai_cli.cli.PromptSession')
def test_handle_context_command(mock_prompt_session):
    """测试处理context命令"""
    mock_prompt_session.return_value = MagicMock()
    
    with patch('ai_cli.display.Console') as mock_console:
        mock_console.return_value = MagicMock()
        
        cli = AICLI()
        
        with patch.object(cli.display, 'show_info') as mock_show_info:
            cli.context_command.handle([])
            mock_show_info.assert_called_once()


@patch('ai_cli.cli.PromptSession')
def test_handle_context_command_with_limit(mock_prompt_session):
    """测试处理context命令（带限制）"""
    mock_prompt_session.return_value = MagicMock()
    
    with patch('ai_cli.display.Console') as mock_console:
        mock_console.return_value = MagicMock()
        
        cli = AICLI()
        
        with patch.object(cli.display, 'show_info') as mock_show_info:
            cli.context_command.handle(["50"])
            mock_show_info.assert_called_once()
            assert cli.session.max_history == 50
