import pytest
from backend.schemas import IntentContext
from intent_engine.step1_guardrail import guardrail

class TestGuardrail:
    def test_safe_query(self):
        """测试安全查询"""
        context = IntentContext(
            user_id="test_user",
            app_id="Lingxi",
            session_id="test_session",
            raw_query="查比亚迪的存款"
        )
        result = guardrail.check(context)
        assert not result.is_rejected
        assert result.rejection_reason is None
    
    def test_rejected_query(self):
        """测试被拒绝的查询"""
        context = IntentContext(
            user_id="test_user",
            app_id="Lingxi",
            session_id="test_session",
            raw_query="敏感内容"
        )
        result = guardrail.check(context)
        assert result.is_rejected
        assert result.rejection_reason is not None