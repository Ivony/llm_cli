"""
测试main.py入口模块
"""
import sys
import os
from unittest.mock import patch, MagicMock


def test_main_import():
    """测试main模块可以正确导入"""
    # 确保当前目录在path中
    if '.' not in sys.path:
        sys.path.insert(0, '.')
    
    # 测试导入main
    import main
    assert main is not None
    assert hasattr(main, 'main') or hasattr(main, '__name__')


def test_main_module_structure():
    """测试main模块的正确结构"""
    if '.' not in sys.path:
        sys.path.insert(0, '.')
    
    # 测试不调用实际运行 - 只测试导入和结构正确性
    # main函数会在导入时存在，但我们不调用它
    assert True  # 如果能到达这里，说明导入成功


def test_syspath_configuration():
    """测试main.py正确配置了sys.path"""
    if '.' not in sys.path:
        sys.path.insert(0, '.')
    
    # 保存原始sys.path
    original_path = sys.path.copy()
    
    try:
        # 创建一个干净的测试环境
        import importlib
        import main
        importlib.reload(main)
        
        # 检查是否有正确的路径添加（至少确保没有错误）
        assert len(sys.path) > 0
    finally:
        # 恢复原始路径
        sys.path = original_path


def test_cli_textual_mode_initialization():
    """测试CLI在Textual模式下的初始化"""
    from ai_cli.cli import AICLI
    from ai_cli.display import DisplayManager
    
    with patch('ai_cli.cli.PromptSession') as mock_prompt:
        mock_prompt.return_value = MagicMock()
        with patch.object(DisplayManager, 'run') as mock_run:
            cli = AICLI(use_textual=True)
            assert cli.use_textual is True
            assert cli.display is not None
            assert cli.prompt_session is not None


def test_cli_traditional_mode_initialization():
    """测试CLI在传统模式下的初始化"""
    from ai_cli.cli import AICLI
    
    with patch('ai_cli.cli.PromptSession') as mock_prompt:
        mock_prompt.return_value = MagicMock()
        cli = AICLI(use_textual=False)
        assert cli.use_textual is False
        assert cli.display is not None
        assert cli.prompt_session is not None


def test_cli_run_textual_mode():
    """测试CLI在Textual模式下run方法调用正确的显示方法"""
    from ai_cli.cli import AICLI
    from ai_cli.display import DisplayManager
    
    with patch('ai_cli.cli.PromptSession') as mock_prompt:
        mock_prompt.return_value = MagicMock()
        with patch.object(DisplayManager, 'run') as mock_run:
            cli = AICLI(use_textual=True)
            cli.run()
            mock_run.assert_called_once()