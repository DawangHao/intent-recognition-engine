import pytest
from backend.schemas import IntentContext
from intent_engine.step4_intent_core import intent_core

class TestIntentCore:
    def test_process(self):
        """测试意图识别核心处理"""
        context = IntentContext(
            user_id="test_user",
            app_id="Lingxi",
            session_id="test_session",
            raw_query="查比亚迪的存款"
        )
        result = intent_core.process(context)
        assert result.raw_query == "查比亚迪的存款"
        # 测试是否设置了技能ID和置信度
        assert hasattr(result, 'skill_id')
        assert hasattr(result, 'confidence')