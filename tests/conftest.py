import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def base_url():
    """返回后端服务的基础URL"""
    return "http://localhost:8000"

@pytest.fixture
def test_company():
    """返回测试用的企业名称"""
    return "比亚迪"

@pytest.fixture
def test_user_id():
    """返回测试用的用户ID"""
    return "test_user_001"

@pytest.fixture
def test_session_id():
    """返回测试用的会话ID"""
    return "session_001"

@pytest.fixture
def test_app_id():
    """返回测试用的应用ID"""
    return "Lingxi"