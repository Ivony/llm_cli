from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.theme import Theme
from typing import Optional


class DisplayManager:
    """显示管理器"""
    
    def __init__(self, config):
        self.config = config
        self.console = Console(
            theme=self._get_theme(),
            color_system="auto" if config.get("display.color_scheme") == "auto" else "standard"
        )
    
    def _get_theme(self):
        """获取主题"""
        return Theme({
            "user": "green",
            "assistant": "blue",
            "error": "red",
            "info": "cyan",
            "warning": "yellow"
        })
    
    def show_user_input(self, text: str):
        """显示用户输入"""
        self.console.print(f"[bold green]User:[/bold green] {text}")
    
    def show_model_output(self, text: str, provider_name: str = "Assistant"):
        """显示模型输出"""
        self.console.print(f"[bold blue]{provider_name}:[/bold blue] {text}")
    
    def show_error(self, message: str):
        """显示错误信息"""
        self.console.print(f"[bold red]Error:[/bold red] {message}")
    
    def show_info(self, message: str):
        """显示信息"""
        self.console.print(f"[bold cyan]Info:[/bold cyan] {message}")
    
    def show_warning(self, message: str):
        """显示警告"""
        self.console.print(f"[bold yellow]Warning:[/bold yellow] {message}")
    
    def show_loading(self, message: str = "Thinking..."):
        """显示加载状态"""
        progress = Progress(
            SpinnerColumn(),
            TextColumn("{task.description}"),
            console=self.console
        )
        return progress
    
    def clear(self):
        """清屏"""
        self.console.clear()
    
    def show_welcome(self):
        """显示欢迎信息"""
        welcome_text = Text("""
        ┌────────────────────────────────────────────────────────────────┐
        │                     AI Command Line Tool                     │
        │                                                              │
        │  A powerful interactive CLI tool for chatting with LLMs       │
        │                                                              │
        └────────────────────────────────────────────────────────────────┘
        
        Type /help for available commands
        """, style="info")
        self.console.print(welcome_text)
    
    def show_help(self):
        """显示帮助信息"""
        help_text = Text("""
        Available commands:
        
        /help              Show this help message
        /exit              Exit the session
        /clear             Clear the screen
        /history           Show conversation history
        /config            Show current configuration
        /model list        List all models and endpoints
        /model add         Add a new endpoint or provider
        /model remove      Remove an endpoint or provider
        /model set         Set current provider
        /context           Manage context length
        /load              Load local file to context
        
        Model command usage:
        /model list [endpoints|providers]      List specific configurations
        /model add endpoint <base_url> [-n NAME] [-p PROTOCOL]  Add an endpoint
        /model add provider <endpoint> [-k API_KEY] [-n NAME] [-m MODEL]  Add a provider
        /model remove <endpoint|provider> <name>  Remove a configuration
        /model set provider <name>  Set current provider
        
        Load command usage:
        /load <file_path> [-n NAME]  Load local file content to conversation context
        -n, --name: Optional. Friendly name for the file
        """, style="info")
        self.console.print(help_text)
