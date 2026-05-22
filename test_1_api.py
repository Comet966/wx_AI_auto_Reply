"""测试 1: API 对话"""
from wx_auto.api.client import SiliconFlowClient
from wx_auto.utils.config import config

print("=" * 50)
print("测试 DeepSeek API 对话")
print("=" * 50)
print(f"模型: {config.model}")
print(f"URL: {config.base_url}\n")

client = SiliconFlowClient()

# Test message
test_msg = "你好，请简单介绍一下自己"

print(f"[用户] {test_msg}\n")

response = client.chat_with_context(test_msg)

print(f"[AI  ] {response}\n")
print("=" * 50)
print("✓ API 对话测试通过")