"""
显示管理器 - 使用Textual组件和ANSI颜色代码
"""


class DisplayManager:
    """显示管理器 - 使用ANSI颜色代码实现简单的彩色输出"""
    
    COLORS = {
        'green': '\033[92m',
        'blue': '\033[94m',
        'red': '\033[91m',
        'cyan': '\033[96m',
        'yellow': '\033[93m',
        'reset': '\033[0m',
        'bold': '\033[1m'
    }
    
    def __init__(self, config):
        self.config = config
    
    def _print_colored(self, prefix: str, color: str, message: str = ""):
        """打印带颜色的输出"""
        if message:
            print(f"{self.COLORS[color]}{self.COLORS['bold']}{prefix}{self.COLORS['reset']} {message}")
        else:
            print(f"{self.COLORS[color]}{prefix}{self.COLORS['reset']}")
    
    def show_user_input(self, text: str):
        """显示用户输入"""
        self._print_colored("User:", 'green', text)
    
    def show_model_output(self, text: str, provider_name: str = "Assistant"):
        """显示模型输出"""
        self._print_colored(f"{provider_name}:", 'blue', text)
    
    def show_error(self, message: str):
        """显示错误信息"""
        self._print_colored("Error:", 'red', message)
    
    def show_info(self, message: str):
        """显示信息"""
        self._print_colored("Info:", 'cyan', message)
    
    def show_warning(self, message: str):
        """显示警告"""
        self._print_colored("Warning:", 'yellow', message)
    
    def show_loading(self, message: str = "Thinking..."):
        """显示加载状态"""
        self._print_colored(message, 'yellow', "")
    
    def hide_loading(self):
        """隐藏加载状态"""
        pass
    
    def clear(self):
        """清屏"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_welcome(self):
        """显示欢迎信息"""
        welcome_text = """
        ┌────────────────────────────────────────────────────────────────┐
        │                     AI Command Line Tool                     │
        │                                                              │
        │  A powerful interactive CLI tool for chatting with LLMs       │
        │                                                              │
        └────────────────────────────────────────────────────────────────┘
        
        Type /help for available commands
        """
        self._print_colored(welcome_text, 'cyan')
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """
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
        """
        self._print_colored(help_text, 'cyan')
    
    def print(self, *args, **kwargs):
        """通用打印方法"""
        print(*args, **kwargs)


# 为了保持兼容性，SimpleDisplay是DisplayManager的别名
SimpleDisplay = DisplayManager