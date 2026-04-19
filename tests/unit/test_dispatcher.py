import pytest
from backend.schemas import IntentContext
from intent_engine.step5_dispatcher import dispatcher

class TestDispatcher:
    def test_dispatch(self):
        """测试任务分发"""
        context = IntentContext(
            user_id="test_user",
            app_id="Lingxi",
            session_id="test_session",
            raw_query="查比亚迪的存款",
            skill_id="SKILL_DEPOSIT_QUERY_V1",
            confidence=0.9
        )
        result = dispatcher.dispatch(context)
        assert result.raw_query == "查比亚迪的存款"
        # 测试是否设置了action_suggestion
        assert hasattr(result, 'action_suggestion')
        assert 'action' in result.action_suggestion