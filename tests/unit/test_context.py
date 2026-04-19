import pytest
from backend.schemas import IntentContext
from intent_engine.step2_context import context_manager

class TestContextManager:
    def test_load_context(self):
        """测试加载上下文"""
        context = IntentContext(
            user_id="test_user",
            app_id="Lingxi",
            session_id="test_session",
            raw_query="查比亚迪的存款"
        )
        result = context_manager.load_context(context)
        assert result.user_id == "test_user"
        assert result.app_id == "Lingxi"
        assert result.session_id == "test_session"
    
    def test_save_context(self):
        """测试保存上下文"""
        context = IntentContext(
            user_id="test_user",
            app_id="Lingxi",
            session_id="test_session",
            raw_query="查比亚迪的存款"
        )
        result = context_manager.save_context(context)
        # 由于使用的是假Redis，这里只测试方法是否正常执行
        assert result is None