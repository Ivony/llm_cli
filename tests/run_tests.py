import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if __name__ == "__main__":
    # 运行所有测试
    result = pytest.main([
        "-v",
        "tests/"
    ])
    
    # 退出码
    sys.exit(result)
