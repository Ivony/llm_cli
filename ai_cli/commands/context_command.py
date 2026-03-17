from typing import List


class ContextCommand:
    """上下文命令处理器"""
    
    def __init__(self, cli):
        self.cli = cli
        self.config = cli.config
        self.display = cli.display
        self.session = cli.session
    
    def handle(self, args: List[str]):
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
