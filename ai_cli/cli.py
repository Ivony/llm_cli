import sys
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from .config import ConfigManager
from .display import DisplayManager
from .session import SessionManager
from .adapters import adapter_factory


class AICLI:
    """AI命令行工具"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.display = DisplayManager(self.config)
        self.session = SessionManager(self.config, self.display)
        self.prompt_session = PromptSession(
            history=InMemoryHistory(),
            auto_suggest=AutoSuggestFromHistory()
        )
    
    def run(self):
        """运行交互式会话"""
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
        parts = command.strip().split()
        cmd = parts[0].lower()
        
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
            self._handle_model_command(parts[1:] if len(parts) > 1 else [])
        elif cmd == "/context":
            self._handle_context_command(parts[1:] if len(parts) > 1 else [])
        elif cmd == "/load":
            self._handle_load_command(parts[1:] if len(parts) > 1 else [])
        else:
            self.display.show_error(f"Unknown command: {cmd}")
    
    def _handle_model_command(self, args: list):
        """处理模型配置命令"""
        if not args:
            self.display.show_error("Model command requires subcommand")
            self.display.show_info("Usage: /model <list|add|remove|set> [options]")
            return
        
        subcmd = args[0].lower()
        
        if subcmd == "list":
            # 处理列表命令
            if len(args) > 1:
                target = args[1].lower()
                if target == "endpoints":
                    self._list_endpoints()
                elif target == "providers":
                    self._list_providers()
                else:
                    self.display.show_error(f"Unknown target: {target}")
            else:
                # 显示所有配置
                self.display.show_info("=== Endpoints ===")
                self._list_endpoints()
                self.display.show_info("\n=== Providers ===")
                self._list_providers()
        elif subcmd == "add":
            # 处理添加命令
            if len(args) < 2:
                self.display.show_error("Usage: /model add <endpoint|provider> [options]")
                return
            
            target = args[1].lower()
            if target == "endpoint":
                self._add_endpoint(args[2:])
            elif target == "provider":
                self._add_provider(args[2:])
            else:
                self.display.show_error(f"Unknown target: {target}")
        elif subcmd == "remove":
            # 处理移除命令
            if len(args) < 2:
                self.display.show_error("Usage: /model remove <endpoint|provider> <name>")
                return
            
            target = args[1].lower()
            if len(args) > 2:
                name = args[2]
                if target == "endpoint":
                    self._remove_endpoint(name)
                elif target == "provider":
                    self._remove_provider(name)
                else:
                    self.display.show_error(f"Unknown target: {target}")
            else:
                self.display.show_error("Name required")
        elif subcmd == "set":
            # 处理设置命令
            if len(args) < 2:
                self.display.show_error("Usage: /model set <provider> <name>")
                return
            
            target = args[1].lower()
            if target == "provider" and len(args) > 2:
                self.session.set_provider(args[2])
            else:
                self.display.show_error("Usage: /model set provider <name>")
        else:
            self.display.show_error(f"Unknown model command: {subcmd}")
    
    def _handle_context_command(self, args: list):
        """处理上下文命令"""
        if not args:
            self.display.show_info(f"Current max history: {self.session.max_history}")
        else:
            try:
                new_limit = int(args[0])
                self.session.max_history = new_limit
                self.config.set("general.max_history", new_limit)
                self.display.show_info(f"Set max history to: {new_limit}")
            except ValueError:
                self.display.show_error("Invalid context limit")
    
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
                self.display.show_model_output(content)
    
    def _show_config(self):
        """显示配置"""
        config = self.config.config
        self.display.show_info("Current configuration:")
        for section, values in config.items():
            self.display.console.print(f"[bold cyan]{section}:[/bold cyan]")
            for key, value in values.items():
                if isinstance(value, dict):
                    self.display.console.print(f"  [bold]{key}:[/bold]")
                    for k, v in value.items():
                        if k == "api_key" and v:
                            v = "***" + v[-4:]
                        self.display.console.print(f"    {k}: {v}")
                else:
                    self.display.console.print(f"  {key}: {value}")
    
    def _list_providers(self):
        """列出所有模型提供程序"""
        providers = self.config.config.get("providers", {})
        if not providers:
            self.display.show_info("No providers configured")
            return
        
        self.display.show_info("Available providers:")
        for name, config in providers.items():
            current = "[bold green] (current)[/bold green]" if name == self.session.current_provider else ""
            self.display.console.print(f"[bold]{name}{current}:[/bold]")
            self.display.console.print(f"  Endpoint: {config.get('endpoint')}")
            self.display.console.print(f"  Model: {config.get('default_model')}")
            if config.get('api_key'):
                self.display.console.print(f"  API Key: ***{config.get('api_key')[-4:]}")
            else:
                self.display.console.print(f"  API Key: [red]Not set[/red]")
    
    def _list_endpoints(self):
        """列出所有端点配置"""
        endpoints = self.config.config.get("endpoints", {})
        if not endpoints:
            self.display.show_info("No endpoints configured")
            return
        
        self.display.show_info("Available endpoints:")
        for name, config in endpoints.items():
            self.display.console.print(f"[bold]{name}:[/bold]")
            self.display.console.print(f"  Protocol: {config.get('protocol')}")
            self.display.console.print(f"  Base URL: {config.get('base_url')}")
    
    def _add_endpoint(self, args: list):
        """添加端点配置"""
        import argparse
        
        parser = argparse.ArgumentParser(description="Add a new endpoint")
        parser.add_argument("base_url", help="The API base URL")
        parser.add_argument("-n", "--name", help="A friendly name for the endpoint")
        parser.add_argument("-p", "--protocol", default="openai", help="The protocol (default: openai)")
        
        try:
            parsed_args = parser.parse_args(args)
            base_url = parsed_args.base_url
            name = parsed_args.name
            protocol = parsed_args.protocol
            
            try:
                self.config.add_endpoint(
                    base_url=base_url,
                    name=name,
                    protocol=protocol
                )
                endpoint_key = name if name else base_url
                self.display.show_info(f"Added endpoint: {endpoint_key}")
            except ValueError as e:
                # 检查是否是name重复
                if "name" in str(e) and name:
                    # 询问用户是否修改
                    self.display.show_warning(f"Endpoint with name '{name}' already exists. Do you want to modify it? (y/n)")
                    user_input = input().strip().lower()
                    if user_input == "y":
                        # 移除旧的端点
                        self.config.remove_endpoint(name)
                        # 添加新的端点
                        self.config.add_endpoint(
                            base_url=base_url,
                            name=name,
                            protocol=protocol
                        )
                        self.display.show_info(f"Modified endpoint: {name}")
                else:
                    self.display.show_error(str(e))
        except SystemExit:
            # argparse 会在解析失败时调用 sys.exit()
            self.display.show_error("Usage: /endpoint add <base_url> [-n NAME] [-p PROTOCOL]")
            return
    
    def _remove_endpoint(self, name: str):
        """移除端点配置"""
        self.config.remove_endpoint(name)
        self.display.show_info(f"Removed endpoint: {name}")
    
    def _add_provider(self, args: list):
        """添加模型提供程序"""
        import argparse
        
        parser = argparse.ArgumentParser(description="Add a new provider")
        parser.add_argument("endpoint", help="Endpoint name or base URL")
        parser.add_argument("-k", "--api-key", default="", help="API key for authentication")
        parser.add_argument("-n", "--name", help="Provider name (default: endpoint name)")
        parser.add_argument("-m", "--model", default="gpt-3.5-turbo", help="Default model to use (default: gpt-3.5-turbo)")
        
        try:
            parsed_args = parser.parse_args(args)
            endpoint = parsed_args.endpoint
            api_key = parsed_args.api_key
            name = parsed_args.name
            model = parsed_args.model
            
            # 如果没有指定名称，默认使用endpoint名称
            if not name:
                # 检查endpoint是否是base_url
                endpoint_key = self.config.get_endpoint_by_base_url(endpoint)
                if endpoint_key:
                    # 如果是base_url，使用对应的端点名称
                    endpoint_config = self.config.get_endpoint_config(endpoint_key)
                    name = endpoint_config.get("name", endpoint_key)
                else:
                    # 否则使用endpoint作为名称
                    name = endpoint
            
            # 检查provider名称是否已存在
            providers = self.config.config.get("providers", {})
            if name in providers:
                self.display.show_error(f"Provider with name '{name}' already exists")
                return
            
            self.config.add_provider(
                name=name,
                endpoint=endpoint,
                api_key=api_key,
                default_model=model,
                temperature=0.7,
                max_tokens=1000
            )
            self.display.show_info(f"Added provider: {name}")
        except SystemExit:
            # argparse 会在解析失败时调用 sys.exit()
            self.display.show_error("Usage: /provider add <endpoint> [-k API_KEY] [-n NAME] [-m MODEL]")
            return
    
    def _remove_provider(self, name: str):
        """移除模型提供程序"""
        self.config.remove_provider(name)
        self.display.show_info(f"Removed provider: {name}")
    
    def _handle_load_command(self, args: list):
        """加载本地文件到上下文"""
        if not args:
            self.display.show_error("Usage: /load <file_path>")
            return
        
        file_path = args[0]
        
        try:
            # 读取文件内容
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 构建文件内容消息
            file_message = f"[FILE]{file_path}[/FILE]\n{content}"
            
            # 添加到历史记录
            self.session.add_message("user", file_message)
            
            # 显示成功信息
            self.display.show_info(f"Loaded file: {file_path}")
            self.display.show_user_input(f"[FILE] {file_path}")
            
        except FileNotFoundError:
            self.display.show_error(f"File not found: {file_path}")
        except Exception as e:
            self.display.show_error(f"Failed to load file: {e}")

    def _handle_input(self, user_input: str):
        """处理用户输入"""
        # 显示用户输入
        self.display.show_user_input(user_input)
        
        # 添加到历史记录
        self.session.add_message("user", user_input)
        
        # 获取当前提供程序配置
        provider_config = self.session.get_provider_config()
        if not provider_config.get("api_key"):
            self.display.show_error("API key not set for current provider")
            return
        
        # 创建适配器
        try:
            adapter = adapter_factory(
                provider_config["protocol"],
                provider_config
            )
        except Exception as e:
            self.display.show_error(f"Failed to create adapter: {e}")
            return
        
        # 显示加载状态
        with self.display.show_loading() as progress:
            progress.add_task("Generating response...", total=None)
            
            # 构建消息历史
            messages = self.session.get_messages()
            
            try:
                # 调用模型
                response = adapter.chat(messages)
                
                # 显示模型输出
                self.display.show_model_output(response)
                
                # 添加到历史记录
                self.session.add_message("assistant", response)
                
            except Exception as e:
                self.display.show_error(f"Failed to get response: {e}")


def main():
    """主函数"""
    cli = AICLI()
    cli.run()


if __name__ == "__main__":
    main()
