import argparse
from typing import List


class LoadCommand:
    """加载文件命令处理器"""
    
    def __init__(self, cli):
        self.cli = cli
        self.config = cli.config
        self.display = cli.display
        self.session = cli.session
    
    def handle(self, args: List[str]):
        """加载本地文件到上下文"""
        parser = argparse.ArgumentParser(description="Load local file to context")
        parser.add_argument("file_path", help="Path to the file to load")
        parser.add_argument("-n", "--name", help="Friendly name for the file")
        
        try:
            parsed_args = parser.parse_args(args)
            file_path = parsed_args.file_path
            file_name = parsed_args.name or file_path
            
            # 读取文件内容
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 构建文件内容消息
            file_message = f"[FILE]{file_name}[/FILE]\n{content}"
            
            # 添加到历史记录
            self.session.add_message("user", file_message)
            
            # 显示成功信息
            self.display.show_info(f"Loaded file: {file_path} as {file_name}")
            self.display.show_user_input(f"[FILE] {file_name}")
            
        except SystemExit:
            self.display.show_error("Usage: /load <file_path> [-n NAME]")
            return
        except FileNotFoundError:
            self.display.show_error(f"File not found: {file_path}")
        except Exception as e:
            self.display.show_error(f"Failed to load file: {e}")
