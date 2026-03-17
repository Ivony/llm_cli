# AI 命令行工具

一个功能强大的交互式命令行工具，用于与大型语言模型（LLMs）进行对话。

## 功能特性

- 与大型语言模型的交互式对话
- 支持多个模型提供程序
- 管理不同 API URL 的端点
- 丰富的终端输出格式化
- 会话历史管理
- 上下文长度控制

## 安装

### 前提条件

- Python 3.7+
- Pip

### 安装步骤

1. 克隆仓库：
   ```bash
   git clone <仓库地址>
   cd ai_cli
   ```

2. 安装依赖：
   ```bash
   pip install -e .
   ```

3. 运行工具：
   ```bash
   ai-cli
   # 或者
   python main.py
   # 或者
   python -m ai_cli.cli
   ```

## 使用方法

### 基本命令

- `/help` - 显示帮助信息
- `/exit` - 退出会话
- `/clear` - 清屏
- `/history` - 显示对话历史
- `/config` - 显示当前配置

### 模型配置管理

通过统一的命令结构管理端点和提供程序。

#### 列出配置
- `/model list` - 列出所有端点和提供程序
- `/model list endpoints` - 仅列出端点
- `/model list providers` - 仅列出提供程序

#### 添加配置
- `/model add endpoint <base_url> [-n NAME] [-p PROTOCOL]` - 添加新端点
  - `base_url`: 必填。API 基础 URL
  - `-n, --name`: 可选。端点的友好名称
  - `-p, --protocol`: 可选。协议（默认：openai）

- `/model add provider <endpoint> [-k API_KEY] [-n NAME] [-m MODEL]` - 添加新提供程序
  - `endpoint`: 必填。端点名称或基础 URL
  - `-k, --api-key`: 可选。用于认证的 API 密钥
  - `-n, --name`: 可选。提供程序名称（默认：端点名称）
  - `-m, --model`: 可选。默认使用的模型（默认：gpt-3.5-turbo）

#### 删除配置
- `/model remove endpoint <name>` - 删除端点
- `/model remove provider <name>` - 删除提供程序

#### 设置当前提供程序
- `/model set provider <name>` - 设置当前提供程序

## 使用示例

### 添加端点

```bash
# 添加带名称和协议的端点
/model add endpoint YOUR_API_ENDPOINT -n my-endpoint -p openai

# 添加不带名称的端点（使用 base_url 作为标识符）
/model add endpoint http://api.openai.com/v1

# 只指定名称添加端点
/model add endpoint http://api.example.com/v1 -n example-endpoint
```

### 添加提供程序

```bash
# 使用端点名称添加提供程序
/model add provider my-endpoint -k YOUR_API_KEY -n my-provider -m gpt-3.5-turbo

# 使用端点 base_url 添加提供程序
/model add provider http://api.openai.com/v1 -k YOUR_API_KEY -n openai-provider -m gpt-4

# 使用最小参数添加提供程序
/model add provider my-endpoint -k YOUR_API_KEY
```

### 列出配置

```bash
# 列出所有配置
/model list

# 仅列出端点
/model list endpoints

# 仅列出提供程序
/model list providers
```

### 删除配置

```bash
# 删除端点
/model remove endpoint my-endpoint

# 删除提供程序
/model remove provider my-provider
```

### 设置当前提供程序

```bash
/model set provider my-provider
user> 你好
```

## 配置

配置存储在 `config.yaml` 文件中。您可以手动编辑它，或使用命令行命令来管理它。

## 测试

运行测试套件：

```bash
python -m pytest tests/
```

## 许可证

[MIT](LICENSE)
