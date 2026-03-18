import argparse
from typing import List


class ModelCommand:
    """模型配置命令处理器"""
    
    def __init__(self, cli):
        self.cli = cli
        self.config = cli.config
        self.display = cli.display
        self.session = cli.session
    
    def handle(self, args: List[str]):
        """处理模型配置命令"""
        if not args:
            self.display.show_error("Model command requires subcommand")
            self.display.show_info("Usage: /model <list|add|remove|set> [options]")
            return
        
        subcmd = args[0].lower()
        
        if subcmd == "list":
            self._handle_list(args[1:])
        elif subcmd == "add":
            self._handle_add(args[1:])
        elif subcmd == "remove":
            self._handle_remove(args[1:])
        elif subcmd == "set":
            self._handle_set(args[1:])
        else:
            self.display.show_error(f"Unknown model command: {subcmd}")
    
    def _handle_list(self, args: List[str]):
        """处理列表命令"""
        if len(args) > 0:
            target = args[0].lower()
            if target == "endpoints":
                self.display.console.print("[bold cyan]=== 端点配置 ===[/bold cyan]")
                self._list_endpoints()
            elif target == "providers":
                self.display.console.print("[bold green]=== 提供程序配置 ===[/bold green]")
                self._list_providers()
            else:
                self.display.show_error(f"Unknown target: {target}")
        else:
            # 显示所有配置，先显示提供程序再显示端点
            self.display.console.print("[bold green]=== 提供程序配置 ===[/bold green]")
            self._list_providers()
            self.display.console.print()
            self.display.console.print("[bold cyan]=== 端点配置 ===[/bold cyan]")
            self._list_endpoints()
    
    def _handle_add(self, args: List[str]):
        """处理添加命令"""
        if len(args) < 1:
            self.display.show_error("Usage: /model add <endpoint|provider> [options]")
            return
        
        target = args[0].lower()
        if target == "endpoint":
            self._add_endpoint(args[1:])
        elif target == "provider":
            self._add_provider(args[1:])
        else:
            self.display.show_error(f"Unknown target: {target}")
    
    def _handle_remove(self, args: List[str]):
        """处理移除命令"""
        if len(args) < 2:
            self.display.show_error("Usage: /model remove <endpoint|provider> <name>")
            return
        
        target = args[0].lower()
        if len(args) > 1:
            name = args[1]
            if target == "endpoint":
                self._remove_endpoint(name)
            elif target == "provider":
                self._remove_provider(name)
            else:
                self.display.show_error(f"Unknown target: {target}")
        else:
            self.display.show_error("Name required")
    
    def _handle_set(self, args: List[str]):
        """处理设置命令"""
        if len(args) < 2:
            self.display.show_error("Usage: /model set <provider> <name>")
            return
        
        target = args[0].lower()
        if target == "provider" and len(args) > 1:
            self.session.set_provider(args[1])
        else:
            self.display.show_error("Usage: /model set provider <name>")
    
    def _list_providers(self):
        """列出所有模型提供程序"""
        providers = self.config.config.get("providers", {})
        if not providers:
            self.display.show_info("No providers configured")
            return
        
        # 分离当前提供程序和其他提供程序
        current_provider = None
        other_providers = []
        
        for name, config in providers.items():
            if name == self.session.current_provider:
                current_provider = (name, config)
            else:
                other_providers.append((name, config))
        
        # 先显示当前提供程序
        if current_provider:
            name, config = current_provider
            current = " [bold green](当前)[/bold green]"
            model = config.get('default_model')
            api_key = config.get('api_key', '')
            api_key_display = f"***{api_key[-4:]}" if api_key else "[gray]未设置[/gray]"
            
            # 显示提供程序基本信息，当前使用的提供程序使用更明显的强调
            self.display.console.print(f"[bold green bg_black]{name}{current}[/bold green bg_black] | {model} | {api_key_display}")
            
            # 显示关联端点信息
            endpoint = config.get('endpoint')
            endpoints = self.config.config.get("endpoints", {})
            endpoint_config = endpoints.get(endpoint)
            if endpoint_config:
                protocol = endpoint_config.get('protocol')
                base_url = endpoint_config.get('base_url')
                self.display.console.print(f"  └── 端点: {endpoint} ({protocol}, {base_url})")
            else:
                # 尝试通过base_url查找端点
                endpoint_key = self.config.get_endpoint_by_base_url(endpoint)
                if endpoint_key:
                    endpoint_config = self.config.get_endpoint_config(endpoint_key)
                    protocol = endpoint_config.get('protocol')
                    base_url = endpoint_config.get('base_url')
                    self.display.console.print(f"  └── 端点: {endpoint_key} ({protocol}, {base_url})")
                else:
                    self.display.console.print(f"  └── 端点: {endpoint} [gray](未找到)[/gray]")
            
            # 如果还有其他提供程序，添加空行
            if other_providers:
                self.display.console.print()
        
        # 显示其他提供程序
        for i, (name, config) in enumerate(other_providers):
            # 在项与项之间添加空行（除了第一项）
            if i > 0:
                self.display.console.print()
                
            color = "blue"
            model = config.get('default_model')
            api_key = config.get('api_key', '')
            api_key_display = f"***{api_key[-4:]}" if api_key else "[gray]未设置[/gray]"
            
            # 显示提供程序基本信息
            self.display.console.print(f"[bold {color}]{name}[/bold {color}] | {model} | {api_key_display}")
            
            # 显示关联端点信息
            endpoint = config.get('endpoint')
            endpoints = self.config.config.get("endpoints", {})
            endpoint_config = endpoints.get(endpoint)
            if endpoint_config:
                protocol = endpoint_config.get('protocol')
                base_url = endpoint_config.get('base_url')
                self.display.console.print(f"  └── 端点: {endpoint} ({protocol}, {base_url})")
            else:
                # 尝试通过base_url查找端点
                endpoint_key = self.config.get_endpoint_by_base_url(endpoint)
                if endpoint_key:
                    endpoint_config = self.config.get_endpoint_config(endpoint_key)
                    protocol = endpoint_config.get('protocol')
                    base_url = endpoint_config.get('base_url')
                    self.display.console.print(f"  └── 端点: {endpoint_key} ({protocol}, {base_url})")
                else:
                    self.display.console.print(f"  └── 端点: {endpoint} [gray](未找到)[/gray]")
    
    def _list_endpoints(self):
        """列出所有端点配置"""
        endpoints = self.config.config.get("endpoints", {})
        if not endpoints:
            self.display.show_info("No endpoints configured")
            return
        
        for i, (name, config) in enumerate(endpoints.items()):
            # 在项与项之间添加空行（除了第一项）
            if i > 0:
                self.display.console.print()
                
            protocol = config.get('protocol')
            base_url = config.get('base_url')
            
            # 显示端点基本信息
            self.display.console.print(f"[bold cyan]{name}[/bold cyan] | {protocol} | {base_url}")
            
            # 查找使用该端点的提供程序
            providers = self.config.config.get("providers", {})
            using_providers = []
            for provider_name, provider_config in providers.items():
                provider_endpoint = provider_config.get('endpoint')
                # 检查是否使用当前端点（通过名称或base_url）
                if provider_endpoint == name or provider_endpoint == base_url:
                    current = " (current)" if provider_name == self.session.current_provider else ""
                    color = "green" if provider_name == self.session.current_provider else ""
                    using_providers.append(f"{provider_name}{current}")
            
            # 显示使用该端点的提供程序
            if using_providers:
                providers_str = ", ".join(using_providers)
                self.display.console.print(f"  └── 使用: {providers_str}")
            else:
                self.display.console.print(f"  └── 使用: [gray]无[/gray]")
    
    def _add_endpoint(self, args: List[str]):
        """添加端点配置"""
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
    
    def _add_provider(self, args: List[str]):
        """添加模型提供程序"""
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
