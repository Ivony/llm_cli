# 单元测试设计文档

## 1. 测试范围与目标

### 1.1 测试范围
本单元测试覆盖AI命令行工具的核心功能模块，包括：
- 适配器层（Adapters）：OpenAI协议适配器
- 配置管理层（Config）：配置加载、保存、端点管理
- 会话管理层（Session）：消息历史、提供程序切换
- CLI层：命令处理、交互逻辑
- 显示层（Display）：用户界面展示
- 主入口模块（Main）：程序初始化逻辑

### 1.2 测试目标
- **代码质量保障**：确保各模块功能正确性
- **回归测试**：修改代码后快速验证功能完整性
- **功能覆盖**：核心业务逻辑覆盖率达到90%以上
- **文档化**：作为功能规范和使用示例

### 1.3 不测试范围
- 实际大模型API调用（使用Mock替代）
- Textual UI交互测试（单元测试阶段）
- 性能测试和压力测试
- 端到端集成测试


## 2. 测试环境配置

### 2.1 技术栈
| 组件 | 版本/说明 |
|------|----------|
| Python | 3.10+ |
| pytest | 测试框架 |
| unittest.mock | Mock对象 |
| yaml | 配置文件处理 |
| httpx | HTTP客户端（异步） |
| textual | UI框架 |

### 2.2 依赖安装
```bash
pip install pytest pyyaml httpx textual prompt_toolkit
```

### 2.3 环境要求
- 支持Windows/macOS/Linux
- 临时文件读写权限
- 不需要真实网络连接（所有外部调用均被Mock）
- 不需要真实API密钥

### 2.4 目录结构
```
ai_cli/
├── tests/
│   ├── run_tests.py          # 测试执行入口
│   ├── test_adapters.py      # 适配器测试
│   ├── test_cli.py           # CLI测试
│   ├── test_config.py        # 配置测试
│   ├── test_display.py       # 显示测试
│   ├── test_endpoints.py     # 端点测试
│   ├── test_main.py          # 主入口测试
│   └── test_session.py       # 会话测试
```


## 3. 测试用例设计原则

### 3.1 设计原则
1. **单一职责**：每个测试用例只验证一个功能点
2. **独立性**：测试用例之间不相互依赖
3. **可重复性**：每次运行结果一致（使用临时文件、Mock）
4. **清晰命名**：`test_模块_功能[_场景]` 命名规范
5. **文档化**：每个测试用例包含清晰的docstring说明

### 3.2 测试策略
| 测试类型 | 实现方式 |
|---------|----------|
| **功能测试** | 验证输入输出正确性 |
| **边界测试** | 空值、最大值、异常值 |
| **Mock测试** | 外部依赖隔离 |
| **异常测试** | 验证错误处理逻辑 |
| **状态测试** | 对象状态变化验证 |

### 3.3 Mock策略
- **外部API**：完全Mock，不发起真实网络请求
- **文件IO**：使用`tempfile`创建临时文件
- **系统调用**：如`os.system`、`sys.exit`使用Mock
- **UI组件**：Textual App运行时采用Mock


## 4. 现有测试用例清单

### 4.1 适配器模块（test_adapters.py）
| 测试用例 | 覆盖功能 | 断言点 |
|---------|---------|--------|
| `test_adapter_factory` | 适配器工厂模式 | 返回正确类型的适配器实例 |
| `test_openai_adapter_initialization` | OpenAI适配器初始化 | api_key/model/base_url正确设置 |
| `test_openai_adapter_get_model_info` | 获取模型信息 | 返回包含正确字段的字典 |

### 4.2 CLI模块（test_cli.py）
| 测试用例 | 覆盖功能 | 断言点 |
|---------|---------|--------|
| `test_cli_initialization` | CLI初始化 | config/display/session/prompt_session创建 |
| `test_handle_command_help` | /help命令 | 调用display.show_help() |
| `test_handle_command_exit` | /exit命令 | 调用sys.exit(0) |
| `test_handle_command_clear` | /clear命令 | 调用display.clear() |
| `test_handle_command_history` | /history命令 | 调用内部_show_history方法 |
| `test_handle_command_config` | /config命令 | 调用内部_show_config方法 |
| `test_handle_model_command_list` | model list命令 | 调用_list_providers/_list_endpoints |
| `test_handle_model_command_add_provider` | model add命令 | 调用_add_provider并传递参数 |
| `test_handle_model_command_remove_provider` | model remove命令 | 调用_remove_provider并传递参数 |
| `test_handle_model_command_set_provider` | model set命令 | 调用session.set_provider |
| `test_handle_context_command` | context命令 | 显示当前上下文限制 |
| `test_handle_context_command_with_limit` | context N命令 | 更新max_history配置 |

### 4.3 配置模块（test_config.py）
| 测试用例 | 覆盖功能 | 断言点 |
|---------|---------|--------|
| `test_config_loading` | 配置文件加载 | 正确读取yaml配置 |
| `test_config_saving` | 配置保存 | 持久化到文件后可重新读取 |
| `test_provider_management` | 提供程序增删 | add/remove后配置正确 |
| `test_env_var_resolution` | 环境变量解析 | API_KEY从环境变量正确读取 |

### 4.4 端点模块（test_endpoints.py）
| 测试用例 | 覆盖功能 | 断言点 |
|---------|---------|--------|
| `test_add_endpoint_with_name` | 添加指定名称端点 | endpoints字典包含正确条目 |
| `test_add_endpoint_without_name` | 添加无名端点 | 使用base_url作为key |
| `test_add_endpoint_without_protocol` | 默认协议 | protocol默认为openai |
| `test_add_duplicate_base_url` | 重复base_url检测 | 抛出ValueError |
| `test_add_duplicate_name` | 重复名称检测 | 抛出ValueError |
| `test_remove_endpoint` | 移除端点 | remove后配置中不存在 |
| `test_get_endpoint_config` | 获取端点配置 | 返回正确的配置字典 |
| `test_get_endpoint_by_base_url` | base_url查找 | 通过url找到对应端点key |

### 4.5 会话模块（test_session.py）
| 测试用例 | 覆盖功能 | 断言点 |
|---------|---------|--------|
| `test_session_initialization` | 会话初始化 | provider/history/max_history正确 |
| `test_message_management` | 消息增删/限制 | add后数量正确，超限制截断 |
| `test_provider_management` | 提供程序切换 | set后current_provider更新 |

### 4.6 显示模块（test_display.py）
| 测试用例 | 覆盖功能 | 断言点 |
|---------|---------|--------|
| `test_display_initialization` | DisplayManager初始化 | config属性正确设置 |
| `test_show_user_input` | 用户消息显示 | 调用print函数输出 |
| `test_show_model_output` | 模型输出显示 | 调用print函数输出 |
| `test_show_error` | 错误信息显示 | 调用print函数输出 |
| `test_show_info` | 信息显示 | 调用print函数输出 |
| `test_show_warning` | 警告显示 | 调用print函数输出 |
| `test_clear` | 清屏功能 | 调用os.system |
| `test_show_welcome` | 欢迎消息 | 调用print函数输出 |
| `test_show_help` | 帮助显示 | 调用print函数输出 |

### 4.7 主入口模块（test_main.py）
| 测试用例 | 覆盖功能 | 断言点 |
|---------|---------|--------|
| `test_main_import` | main模块导入 | 无ImportError |
| `test_main_module_structure` | 模块结构 | 导入成功即通过 |
| `test_syspath_configuration` | sys.path配置 | 无导入错误 |
| `test_cli_textual_mode_initialization` | Textual模式 | use_textual=True |
| `test_cli_traditional_mode_initialization` | 传统模式 | use_textual=False |
| `test_cli_run_textual_mode` | run方法调用 | 调用display.run() |

### 4.8 测试覆盖率统计
| 模块 | 测试用例数 | 覆盖率 |
|------|-----------|--------|
| adapters | 3 | 基础覆盖 |
| cli | 14 | 命令全覆盖 |
| config | 4 + 11 | 端点/配置全覆盖 |
| display | 9 | 显示功能全覆盖 |
| session | 3 | 基础覆盖 |
| main | 6 | 入口全覆盖 |
| **合计** | **47** | |


## 5. 测试执行流程

### 5.1 执行方式

#### 方式1：直接执行所有测试
```bash
cd tests
python run_tests.py
```

#### 方式2：pytest执行所有测试
```bash
python -m pytest tests/ -v
```

#### 方式3：执行特定模块测试
```bash
python -m pytest tests/test_cli.py -v
```

#### 方式4：执行单个测试用例
```bash
python -m pytest tests/test_cli.py::test_handle_command_help -v
```

#### 方式5：生成覆盖率报告
```bash
pip install pytest-cov
python -m pytest tests/ --cov=ai_cli --cov-report=html
```

### 5.2 执行顺序
测试框架自动发现和执行，不依赖特定顺序（因测试用例独立）

### 5.3 CI/CD集成建议
```yaml
# GitHub Actions 示例
steps:
  - uses: actions/checkout@v4
  - uses: actions/setup-python@v5
    with:
      python-version: "3.12"
  - run: pip install -r requirements.txt
  - run: python -m pytest tests/ -v  # 阻塞直到完成
  - name: Upload coverage
    uses: codecov/codecov-action@v3
```


## 6. 测试结果评估标准

### 6.1 通过标准
| 指标 | 要求 |
|------|------|
| **通过率** | 100% (47/47) |
| **错误数** | 0 errors |
| **失败数** | 0 failures |
| **执行时间** | < 10秒 |

### 6.2 失败处理
```
测试失败 → 记录失败信息 → 定位问题 → 修复代码 → 重新运行 → 验证通过
        ↘ 若是测试用例问题 → 更新测试用例
```

### 6.3 结果输出示例
```
============================= test session starts =============================
collected 47 items

tests/test_adapters.py::test_adapter_factory PASSED                      [  2%]
tests/test_adapters.py::test_openai_adapter_initialization PASSED        [  4%]
...
tests/test_session.py::test_provider_management PASSED                   [100%]

============================= 47 passed in 4.88s ==============================
```


## 7. 缺陷管理流程

### 7.1 缺陷分类
| 严重级别 | 定义 | 处理优先级 |
|---------|------|-----------|
| **Critical** | 程序崩溃、数据丢失 | P0 |
| **Major** | 核心功能失效 | P1 |
| **Minor** | 次要功能异常 | P2 |
| **Trivial** | UI/提示文字问题 | P3 |

### 7.2 修复流程
1. **发现缺陷**：测试失败或用户反馈
2. **复现缺陷**：确定触发条件
3. **定位根因**：使用调试工具/print定位
4. **修复代码**：修改最少代码解决问题
5. **回归测试**：运行所有相关测试
6. **更新测试**：必要时新增/修改测试用例
7. **提交代码**：附带测试通过证明


## 8. 测试维护策略

### 8.1 新增功能
- **先写测试**：TDD（测试驱动开发）原则
- **覆盖新功能**：至少覆盖正向路径
- **异常场景**：考虑错误处理路径
- **文档同步**：更新本文档

### 8.2 代码重构
- **先保证测试全过**：重构前运行所有测试
- **保持行为不变**：重构后所有测试必须全过
- **更新测试**：接口变化时同步更新测试

### 8.3 定期回顾
- **每周**：快速扫测试覆盖率报告
- **每月**：审视测试策略和覆盖范围
- **每版本**：完整的测试覆盖评审

### 8.4 最佳实践
```python
# 👍 好的测试
def test_handle_command_help():
    """测试处理help命令"""  # 清晰说明
    cli = AICLI()
    with patch.object(cli.display, 'show_help') as mock:  # 精确Mock
        cli._handle_command("/help")
        mock.assert_called_once()  # 明确断言
```

```python
# 👎 避免的写法
def test_help():
    cli = AICLI()
    cli._handle_command("/help")
    # 没有断言，等于没测
```


## 附录：测试运行脚本

```python
# tests/run_tests.py
import pytest
import sys

def main():
    """运行所有单元测试"""
    args = [
        '-v',           # 详细输出
        '-x',           # 遇错即停
        '--tb=short',   # 简短的回溯信息
        'tests/'        # 测试目录
    ]
    
    # 允许通过命令行传递额外参数
    args.extend(sys.argv[1:])
    
    print("=" * 60)
    print("Running AI CLI Unit Tests")
    print("=" * 60)
    
    exit_code = pytest.main(args)
    
    print("\n" + "=" * 60)
    if exit_code == 0:
        print("✓ All tests passed!")
    else:
        print(f"✗ Test failed with exit code: {exit_code}")
    print("=" * 60)
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
```

---

**文档版本**：1.0  
**创建日期**：2024年  
**更新日期**：2024年  
**覆盖测试数**：47个