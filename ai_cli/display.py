"""
显示管理器 - 使用Textual组件实现流式Markdown渲染
"""
import asyncio
from textual.app import App, ComposeResult
from textual.widgets import Static, Markdown, Input, Label, LoadingIndicator
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widget import Widget
from textual.reactive import var
from textual.events import Click
from typing import Optional, List, Dict, Any


class MessageContent(Static):
    """消息内容组件"""
    pass


class Message(Widget):
    """消息组件"""
    
    def __init__(self, role: str, content: str = "", **kwargs):
        super().__init__(**kwargs)
        self.role = role
        self._content = content
        self.border_title = "User" if role == "user" else "Assistant"
        
    def compose(self) -> ComposeResult:
        if self.role == "user":
            yield MessageContent(self._content, classes="user-message")
        else:
            yield Markdown(self._content, classes="assistant-message", id=f"markdown-{self.id}")
    
    def update_content(self, content: str) -> None:
        """更新消息内容"""
        self._content = content
        if self.role == "user":
            self.query_one(MessageContent).update(content)
        else:
            markdown = self.query_one(Markdown)
            markdown.update(content)


class AIChatApp(App):
    """AI聊天应用 - 支持流式Markdown渲染"""
    
    CSS = """
    Screen {
        background: #0d1117;
        color: #c9d1d9;
    }
    
    .header {
        height: 3;
        background: #161b22;
        border-bottom: solid #30363d;
        content-align: center middle;
        color: #58a6ff;
    }
    
    .chat-container {
        height: 100%;
        overflow-y: auto;
        padding: 1;
    }
    
    .message-container {
        margin: 1 0;
        padding: 0 1;
    }
    
    .user-message {
        color: #7ee787;
        background: #11191f;
        border-left: thick #238636;
        padding: 1;
        margin: 0 2 0 0;
    }
    
    .assistant-message {
        color: #c9d1d9;
        background: #11191f;
        border-left: thick #1f6feb;
        padding: 1;
        margin: 0 0 0 2;
    }
    
    .assistant-message Markdown {
        width: 100%;
    }
    
    .input-area {
        height: 3;
        background: #161b22;
        border-top: solid #30363d;
        padding: 0 1;
    }
    
    .prompt-label {
        width: 6;
        content-align: center middle;
        color: #7ee787;
    }
    
    .input-field {
        background: #0d1117;
        color: #c9d1d9;
    }
    
    .input-field:disabled {
        color: #6e7681;
        background: #161b22;
    }
    
    .submit-btn {
        width: 10;
        background: #238636;
        color: white;
        content-align: center middle;
    }
    
    .submit-btn:disabled {
        background: #21262d;
        color: #6e7681;
    }
    
    .footer {
        height: 2;
        background: #161b22;
        border-top: solid #30363d;
        content-align: center middle;
        color: #8b949e;
    }
    
    .loading-indicator {
        height: 2;
        content-align: center middle;
        color: #d29922;
    }
    
    Markdown {
        background: transparent;
    }
    
    Markdown H1, Markdown H2, Markdown H3, Markdown H4, Markdown H5, Markdown H6 {
        color: #58a6ff;
        margin: 1 0;
    }
    
    Markdown CodeBlock {
        background: #161b22;
        border: solid #30363d;
        padding: 1;
        margin: 1 0;
    }
    
    Markdown CodeInline {
        background: #21262d;
        color: #a5d6ff;
        padding: 0 1;
    }
    
    Markdown Bullet, Markdown OrderedList {
        color: #d29922;
    }
    
    Markdown Link {
        color: #58a6ff;
    }
    
    Markdown BlockQuote {
        border-left: thick #30363d;
        color: #8b949e;
        padding-left: 1;
    }
    
    Markdown HorizontalRule {
        background: #30363d;
        height: 1;
        margin: 1 0;
    }
    """
    
    current_stream_message: var[Optional[Message]] = var(None)
    is_streaming: var[bool] = var(False)
    is_busy: var[bool] = var(False)  # 标记是否正在处理请求
    input_buffer: var[str] = var("")
    user_input_event: var[Optional[asyncio.Event]] = var(None)
    
    def __init__(self, cli=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cli = cli
        self.user_input_event = asyncio.Event()
        self._message_id_counter = 0
    
    def compose(self) -> ComposeResult:
        """构建UI"""
        yield Static("AI Command Line Tool", classes="header")
        yield ScrollableContainer(
            Vertical(id="chat-container", classes="chat-container")
        )
        yield Static("Thinking...", classes="loading-indicator", id="loading")
        yield Horizontal(
            Label("user>", classes="prompt-label"),
            Input(placeholder="Type your message here...", classes="input-field", id="user-input"),
            Static("Send", classes="submit-btn", id="submit-btn"),
            classes="input-area"
        )
        yield Static("Type /help for commands | Ctrl+C to exit", classes="footer")
    
    def on_mount(self) -> None:
        """应用启动时"""
        self.query_one("#loading", Static).display = False
        self.query_one("#user-input", Input).focus()
        # 在应用启动后显示欢迎消息
        self.show_welcome()
    
    def watch_is_busy(self, is_busy: bool) -> None:
        """监听is_busy状态变化，更新UI"""
        submit_btn = self.query_one("#submit-btn", Static)
        if is_busy:
            submit_btn.update("Waiting...")
            submit_btn.add_class("disabled")
            submit_btn.styles.opacity = 0.5
        else:
            submit_btn.update("Send")
            submit_btn.remove_class("disabled")
            submit_btn.styles.opacity = 1.0
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """处理用户输入提交"""
        input_text = event.value.strip()
        if not input_text:
            return
        
        # 清空输入框
        event.input.clear()
        
        # 调用统一处理方法
        await self._submit_input(input_text)
    
    async def on_click(self, event: Click) -> None:
        """处理点击事件"""
        from textual.widgets import Static
        
        if isinstance(event.widget, Static) and event.widget.id == "submit-btn":
            if not self.is_busy:
                # 点击发送按钮
                input_field = self.query_one("#user-input", Input)
                input_text = input_field.value.strip()
                if input_text:
                    input_field.clear()
                    await self._submit_input(input_text)
    
    async def _submit_input(self, input_text: str) -> None:
        """统一的输入提交处理"""
        if self.is_busy:
            return
        
        if input_text.startswith("/"):
            await self.handle_command(input_text)
            return
        
        # 设置忙状态
        self.is_busy = True
        
        try:
            # 添加用户消息到界面
            self.add_user_message(input_text)
            
            # 显示加载状态
            self.show_loading()
            
            # 处理输入（在后台任务中）
            await self.handle_user_input(input_text)
        finally:
            # 清除忙状态
            self.is_busy = False
    
    async def handle_command(self, command: str) -> None:
        """处理命令输入"""
        # 隐藏加载状态（如果显示）
        self.hide_loading()
        
        if command == "/exit":
            self.exit()
            return
        elif command == "/clear":
            self.clear_chat()
            return
        elif command == "/help":
            help_text = """
Available commands:
- /help: Show this help message
- /exit: Exit the application
- /clear: Clear the chat history
- /history: Show conversation history
            """
            self.add_system_message(help_text)
            return
        elif self.cli:
            # 其他命令交由CLI处理
            self.add_system_message(f"Executing command: {command}")
            await asyncio.to_thread(self.cli._handle_command, command)
            return
        
        self.add_system_message(f"Unknown command: {command}")
    
    async def handle_user_input(self, user_input: str) -> None:
        """处理用户输入 - 使用后台线程避免UI阻塞"""
        if self.cli:
            try:
                # 获取当前提供程序配置
                provider_config = self.cli.session.get_provider_config()
                if not provider_config.get("api_key"):
                    self.hide_loading()
                    self.add_system_message("API key not set for current provider")
                    return
                
                # 创建适配器
                try:
                    adapter = self.cli.adapter_factory(
                        provider_config["protocol"],
                        provider_config
                    )
                except Exception as e:
                    self.hide_loading()
                    self.add_system_message(f"Failed to create adapter: {e}")
                    return
                
                # 构建消息历史
                messages = self.cli.session.get_messages()
                
                # 获取当前提供程序名称
                provider_name = self.cli.session.get_current_provider()
                
                # 开始流式输出
                self.start_assistant_message()
                
                # 在后台线程中运行适配器调用，并使用队列传递结果
                response_queue = asyncio.Queue()
                
                def stream_worker():
                    """在后台线程中运行的流式请求"""
                    try:
                        for chunk in adapter.chat_stream(messages):
                            response_queue.put_nowait(("chunk", chunk))
                        response_queue.put_nowait(("done", None))
                    except Exception as e:
                        response_queue.put_nowait(("error", str(e)))
                
                # 启动后台线程
                import threading
                worker_thread = threading.Thread(target=stream_worker, daemon=True)
                worker_thread.start()
                
                # 处理队列中的响应
                full_response = ""
                while True:
                    try:
                        msg_type, data = await asyncio.wait_for(response_queue.get(), timeout=0.1)
                        
                        if msg_type == "chunk":
                            full_response += data
                            self.update_assistant_message(full_response)
                        elif msg_type == "done":
                            break
                        elif msg_type == "error":
                            raise Exception(data)
                            
                    except asyncio.TimeoutError:
                        # 超时继续，给UI刷新的机会
                        continue
                
                # 添加到历史记录
                self.cli.session.add_message("assistant", full_response)
                
            except Exception as e:
                self.add_system_message(f"Failed to get response: {str(e)}")
            finally:
                self.hide_loading()
                self.end_assistant_message()
    
    def add_user_message(self, content: str) -> None:
        """添加用户消息"""
        if self.cli:
            self.cli.session.add_message("user", content)
        
        container = self.query_one("#chat-container", Vertical)
        message = Message(role="user", content=content, classes="message-container")
        container.mount(message)
        container.scroll_end(animate=False)
    
    def add_system_message(self, content: str) -> None:
        """添加系统消息"""
        container = self.query_one("#chat-container", Vertical)
        message = Message(role="system", content=f"**System**: {content}", classes="message-container")
        container.mount(message)
        container.scroll_end(animate=False)
    
    def start_assistant_message(self) -> None:
        """开始助手消息（流式输出）"""
        container = self.query_one("#chat-container", Vertical)
        self.current_stream_message = Message(role="assistant", content="", classes="message-container")
        container.mount(self.current_stream_message)
        self.is_streaming = True
    
    def update_assistant_message(self, content: str) -> None:
        """更新助手消息内容（用于流式输出）"""
        if self.current_stream_message:
            self.current_stream_message.update_content(content)
            container = self.query_one("#chat-container", Vertical)
            container.scroll_end(animate=False)
    
    def end_assistant_message(self) -> None:
        """结束助手消息"""
        self.current_stream_message = None
        self.is_streaming = False
    
    def show_loading(self, message: str = "Thinking...") -> None:
        """显示加载状态"""
        loading = self.query_one("#loading", Static)
        loading.update(f" {message}")
        loading.display = True
    
    def hide_loading(self) -> None:
        """隐藏加载状态"""
        loading = self.query_one("#loading", Static)
        loading.display = False
    
    def clear_chat(self) -> None:
        """清除聊天内容"""
        container = self.query_one("#chat-container", Vertical)
        for child in list(container.children):
            child.remove()
    
    def show_welcome(self) -> None:
        """显示欢迎信息"""
        welcome_text = """
# AI Command Line Tool

Welcome! This is an interactive CLI tool for chatting with LLMs.

**Getting started:**
1. Type your message and press Enter to chat
2. Use `/help` to see all commands
3. Use `/exit` to quit the application

**Available commands:**
- `/help` - Show help information
- `/exit` - Exit the application
- `/clear` - Clear chat history
- `/history` - Show conversation history
        """
        self.add_system_message(welcome_text)


class DisplayManager:
    """显示管理器 - 使用Textual App"""
    
    def __init__(self, config, cli=None):
        self.config = config
        self.cli = cli
        self.app = AIChatApp(cli=cli)
    
    def run(self) -> None:
        """运行聊天应用"""
        self.app.run()
    
    def show_user_input(self, text: str) -> None:
        """显示用户输入（非Textual模式下使用）"""
        print(f"\033[92mUser:\033[0m {text}")
    
    def show_model_output(self, text: str, provider_name: str = "Assistant"):
        """显示模型输出（非Textual模式下使用）"""
        print(f"\033[94m{provider_name}:\033[0m {text}")
    
    def show_error(self, message: str) -> None:
        """显示错误信息（非Textual模式下使用）"""
        print(f"\033[91mError:\033[0m {message}")
    
    def show_info(self, message: str) -> None:
        """显示信息（非Textual模式下使用）"""
        print(f"\033[96mInfo:\033[0m {message}")
    
    def show_warning(self, message: str) -> None:
        """显示警告（非Textual模式下使用）"""
        print(f"\033[93mWarning:\033[0m {message}")
    
    def clear(self) -> None:
        """清屏（非Textual模式下使用）"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print(self, *args, **kwargs) -> None:
        """通用打印方法"""
        print(*args, **kwargs)
    
    def show_help(self) -> None:
        """显示帮助信息"""
        help_text = """
AI Command Line Tool - Help
=========================

Commands:
  /help      - Show this help message
  /exit      - Exit the application
  /clear     - Clear the screen
  /history   - Show conversation history
  /config    - Show current configuration
  /model     - Model management commands
    /model list   - List all configured models
    /model add    - Add a new model provider
    /model remove - Remove a model provider
    /model set    - Set current active model
  /context   - Context management (show current context limit)
  /load      - Load file content into context

In Textual mode (GUI):
  - Type your message and press Enter to send
  - Use commands above starting with /
  - Press Ctrl+C to exit

In CLI mode:
  - Tab completion available for commands
  - Use arrow keys to navigate history
  - Press Ctrl+D to exit
"""
        print(help_text)
    
    def show_welcome(self) -> None:
        """显示欢迎信息"""
        welcome = """
╔══════════════════════════════════════════════════════════════╗
║           AI Command Line Tool                              ║
╠══════════════════════════════════════════════════════════════╣
║  Welcome! Type your message and press Enter to chat.        ║
║  Type /help for available commands.                         ║
╚══════════════════════════════════════════════════════════════╝
"""
        print(welcome)
    
    def show_loading(self, message: str = "Thinking...") -> None:
        """显示加载状态"""
        print(f"\033[93m{message}\033[0m", end="\r")
    
    def hide_loading(self) -> None:
        """隐藏加载状态"""
        print(" " * 50, end="\r")