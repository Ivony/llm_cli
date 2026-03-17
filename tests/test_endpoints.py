import unittest
from unittest.mock import patch, mock_open
import yaml
from ai_cli.config import ConfigManager


class TestEndpoints(unittest.TestCase):
    """测试端点管理功能"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建一个临时配置文件路径
        self.config_file = "test_config.yaml"
        # 创建配置管理器
        self.config = ConfigManager(self.config_file)
    
    def tearDown(self):
        """清理测试环境"""
        import os
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
    
    def test_add_endpoint_with_name(self):
        """测试添加指定名称的端点"""
        # 添加端点
        self.config.add_endpoint(
            base_url="https://api.example.com/v1",
            name="test-endpoint",
            protocol="openai"
        )
        
        # 验证端点是否添加成功
        endpoints = self.config.config.get("endpoints", {})
        self.assertIn("test-endpoint", endpoints)
        self.assertEqual(endpoints["test-endpoint"]["protocol"], "openai")
        self.assertEqual(endpoints["test-endpoint"]["base_url"], "https://api.example.com/v1")
    
    def test_add_endpoint_without_name(self):
        """测试添加没有名称的端点（使用base_url作为标识）"""
        base_url = "https://api.example.com/v1"
        # 添加端点
        self.config.add_endpoint(base_url=base_url)
        
        # 验证端点是否添加成功
        endpoints = self.config.config.get("endpoints", {})
        self.assertIn(base_url, endpoints)
        self.assertEqual(endpoints[base_url]["protocol"], "openai")  # 默认protocol
        self.assertEqual(endpoints[base_url]["base_url"], base_url)
    
    def test_add_endpoint_without_protocol(self):
        """测试添加没有指定协议的端点（使用默认协议）"""
        # 添加端点
        self.config.add_endpoint(
            base_url="https://api.example.com/v1",
            name="test-endpoint"
        )
        
        # 验证端点是否添加成功
        endpoints = self.config.config.get("endpoints", {})
        self.assertIn("test-endpoint", endpoints)
        self.assertEqual(endpoints["test-endpoint"]["protocol"], "openai")  # 默认protocol
        self.assertEqual(endpoints["test-endpoint"]["base_url"], "https://api.example.com/v1")
    
    def test_add_duplicate_base_url(self):
        """测试添加重复的base_url"""
        base_url = "https://api.example.com/v1"
        # 添加第一个端点
        self.config.add_endpoint(base_url=base_url, name="test-endpoint1")
        
        # 尝试添加相同base_url的端点，应该抛出异常
        with self.assertRaises(ValueError):
            self.config.add_endpoint(base_url=base_url, name="test-endpoint2")
    
    def test_add_duplicate_name(self):
        """测试添加重复的名称"""
        endpoint_name = "test-endpoint"
        # 添加第一个端点
        self.config.add_endpoint(
            base_url="https://api.example.com/v1",
            name=endpoint_name
        )
        
        # 尝试添加相同名称的端点，应该抛出异常
        with self.assertRaises(ValueError):
            self.config.add_endpoint(
                base_url="https://api.example.com/v2",
                name=endpoint_name
            )
    
    def test_remove_endpoint(self):
        """测试移除端点"""
        # 先添加端点
        self.config.add_endpoint(
            base_url="https://api.example.com/v1",
            name="test-endpoint"
        )
        
        # 验证端点存在
        endpoints = self.config.config.get("endpoints", {})
        self.assertIn("test-endpoint", endpoints)
        
        # 移除端点
        self.config.remove_endpoint("test-endpoint")
        
        # 验证端点已移除
        endpoints = self.config.config.get("endpoints", {})
        self.assertNotIn("test-endpoint", endpoints)
    
    def test_get_endpoint_config(self):
        """测试获取端点配置"""
        # 添加端点
        self.config.add_endpoint(
            base_url="https://api.example.com/v1",
            name="test-endpoint"
        )
        
        # 获取端点配置
        endpoint_config = self.config.get_endpoint_config("test-endpoint")
        
        # 验证配置正确
        self.assertEqual(endpoint_config["protocol"], "openai")
        self.assertEqual(endpoint_config["base_url"], "https://api.example.com/v1")
    
    def test_get_endpoint_by_base_url(self):
        """测试通过base_url获取端点key"""
        base_url = "https://api.example.com/v1"
        # 添加端点
        self.config.add_endpoint(
            base_url=base_url,
            name="test-endpoint"
        )
        
        # 通过base_url获取端点key
        endpoint_key = self.config.get_endpoint_by_base_url(base_url)
        
        # 验证获取成功
        self.assertEqual(endpoint_key, "test-endpoint")
    
    def test_add_provider_with_endpoint_name(self):
        """测试使用端点名称添加提供程序"""
        # 先添加端点
        self.config.add_endpoint(
            base_url="https://api.example.com/v1",
            name="test-endpoint"
        )
        
        # 添加使用该端点的提供程序
        self.config.add_provider(
            name="test-provider",
            endpoint="test-endpoint",
            api_key="test-api-key",
            default_model="gpt-3.5-turbo"
        )
        
        # 验证提供程序是否添加成功
        providers = self.config.config.get("providers", {})
        self.assertIn("test-provider", providers)
        self.assertEqual(providers["test-provider"]["endpoint"], "test-endpoint")
        self.assertEqual(providers["test-provider"]["api_key"], "test-api-key")
    
    def test_add_provider_with_endpoint_base_url(self):
        """测试使用端点base_url添加提供程序"""
        base_url = "https://api.example.com/v1"
        # 先添加端点（不指定名称）
        self.config.add_endpoint(base_url=base_url)
        
        # 添加使用该端点的提供程序（使用base_url作为endpoint参数）
        self.config.add_provider(
            name="test-provider",
            endpoint=base_url,
            api_key="test-api-key",
            default_model="gpt-3.5-turbo"
        )
        
        # 验证提供程序是否添加成功
        providers = self.config.config.get("providers", {})
        self.assertIn("test-provider", providers)
        self.assertEqual(providers["test-provider"]["endpoint"], base_url)
        self.assertEqual(providers["test-provider"]["api_key"], "test-api-key")


if __name__ == "__main__":
    unittest.main()
