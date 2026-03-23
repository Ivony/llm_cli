import sys
from typing import Optional
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from .config import ConfigManager
from .display import DisplayManager
from .session import SessionManager
from .adapters import adapter_factory
from .commands.model_command import ModelCommand
from .commands.context_command import ContextCommand
from .commands.load_command import LoadCommand


class CommandCompleter(Completer):
    """命令补全器"""
    
    def __init__(self):
        # 定义所有可用的命令
        self.commands = [
            "/help",
            "/exit",
            "/clear",
            "/history",
            "/config",
            "/model",
            "/model list",
            "/model add",
            "/model remove",
            "/model set",
            "/context",
            "/load"
        ]
    
    def get_completions(self, document, complete_event):
        """获取补全选项"""
        text = document.text
        if text.startswith("/"):
            # 过滤匹配的命令
            matches = [cmd for cmd in self.commands if cmd.startswith(text)]
            for match in matches:
                yield Completion(match, start_position=-len(text))


class AICLI:
    """AI命令行工具"""
    
    def __init__(self, use_textual: bool = True):
        self.config = ConfigManager()
        self.use_textual = use_textual
        self.display = DisplayManager(self.config, cli=self)
        self.session = SessionManager(self.config, self.display)
        self.adapter_factory = adapter_factory
        
        # 传统CLI模式下的prompt_session（始终创建以保持测试兼容性）
        self.prompt_session = PromptSession(
            history=InMemoryHistory(),
            auto_suggest=AutoSuggestFromHistory(),
            completer=CommandCompleter()
        )
        
        # 初始化命令处理器
        self.model_command = ModelCommand(self)
        self.context_command = ContextCommand(self)
        self.load_command = LoadCommand(self)
    
    def run(self):
        """运行交互式会话"""
        if self.use_textual:
            # Textual模式 - 使用Textual App进行完整的GUI交互
            self.display.app.show_welcome()
            self.display.run()
        else:
            # 传统CLI模式
            self._run_cli_mode()
    
    def _run_cli_mode(self):
        """传统CLI模式"""
        self.display.show_welcome()
        
        while True:
            try:
                user_input = self.prompt_session.prompt(
                    "user> ",
                    enable_history_search=True
                )
                
                if not user_input.strip():
                    continue
                
                # 处理命令
                if user_input.startswith("/"):
                    self._handle_command(user_input)
                else:
                    # 处理普通输入
                    self._handle_input(user_input)
                    
            except KeyboardInterrupt:
                self.display.show_info("Exiting...")
                break
            except EOFError:
                self.display.show_info("Exiting...")
                break
    
    def _handle_command(self, command: str):
        """处理命令"""
        parts = command.split()
        if not parts:
            return
        
        cmd = parts[0]
        
        if cmd == "/help":
            self.display.show_help()
        elif cmd == "/exit":
            self.display.show_info("Exiting...")
            sys.exit(0)
        elif cmd == "/clear":
            self.display.clear()
        elif cmd == "/history":
            self._show_history()
        elif cmd == "/config":
            self._show_config()
        elif cmd == "/model":
            self.model_command.handle(parts[1:] if len(parts) > 1 else [])
        elif cmd == "/context":
            self.context_command.handle(parts[1:] if len(parts) > 1 else [])
        elif cmd == "/load":
            self.load_command.handle(parts[1:] if len(parts) > 1 else [])
        else:
            self.display.show_error(f"Unknown command: {cmd}")
    
    def _show_history(self):
        """显示历史记录"""
        history = self.session.get_messages()
        if not history:
            self.display.show_info("No history available")
            return
        
        for i, msg in enumerate(history):
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                self.display.show_user_input(content)
            else:
                provider_name = self.session.get_current_provider()
                self.display.show_model_output(content, provider_name)
    
    def _show_config(self):
        """显示配置"""
        config = self.config.config
        self.display.show_info("Current configuration:")
        for section, values in config.items():
            self.display.show_info(f"{section}:")
            for key, value in values.items():
                if isinstance(value, dict):
                    self.display.show_info(f"  {key}:")
                    for k, v in value.items():
                        if k == "api_key" and v:
                            v = "***" + v[-4:]
                        self.display.print(f"    {k}: {v}")
                else:
                    self.display.print(f"  {key}: {value}")

    def _handle_input(self, user_input: str):
        """处理用户输入（传统CLI模式下使用）"""
        # 添加到历史记录
        self.session.add_message("user", user_input)
        
        # 获取当前提供程序配置
        provider_config = self.session.get_provider_config()
        if not provider_config.get("api_key"):
            self.display.show_error("API key not set for current provider")
            return
        
        # 创建适配器
        try:
            adapter = self.adapter_factory(
                provider_config["protocol"],
                provider_config
            )
        except Exception as e:
            self.display.show_error(f"Failed to create adapter: {e}")
            return
        
        # 构建消息历史
        messages = self.session.get_messages()
        
        try:
            # 获取当前提供程序名称
            provider_name = self.session.get_current_provider()
            
            # 调用模型（流式）
            self.display.show_loading()
            full_response = ""
            
            # 传统CLI模式下简单显示完整响应
            for chunk in adapter.chat_stream(messages):
                full_response += chunk
            
            self.display.hide_loading()
            self.display.show_model_output(full_response, provider_name)
            
            # 添加到历史记录
            self.session.add_message("assistant", full_response)
            
        except Exception as e:
            self.display.show_error(f"Failed to get response: {e}")


def main():
    """主函数"""
    # 默认使用Textual模式
    cli = AICLI(use_textual=True)
    cli.run()


if __name__ == "__main__":
    main()