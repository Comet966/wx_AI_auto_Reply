"""Test script for SiliconFlow API."""
import sys

sys.path.insert(0, ".")

from wx_auto.api.client import SiliconFlowClient

# Test messages
test_messages = [
    [{"role": "user", "content": "你叫什么'"}],
]


def test_api():
    """Test API connection."""
    print("=== 测试 SiliconFlow API ===\n")

    # Initialize client
    try:
        client = SiliconFlowClient()
        print("✓ 客户端初始化成功\n")
    except Exception as e:
        print(f"✗ 客户端初始化失败: {e}\n")
        return False

    # Test chat
    print("发送测试消息: '你叫什么'\n")
    try:
        response = client.chat(test_messages[0])
        print(f"收到回复: {response}\n")

        if response and len(response) > 0:
            print("✓ API 连接正常\n")
            return True
        else:
            print("✗ API 返回为空\n")
            return False

    except Exception as e:
        print(f"✗ API 调用失败: {e}\n")
        return False


if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)