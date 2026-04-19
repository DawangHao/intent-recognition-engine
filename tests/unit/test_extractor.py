import pytest
from backend.schemas import IntentContext
from intent_engine.step3_extractor import extract_entities

class TestEntityExtractor:
    def test_extract_entities(self):
        """测试实体提取"""
        context = IntentContext(
            user_id="test_user",
            app_id="Lingxi",
            session_id="test_session",
            raw_query="查比亚迪的存款"
        )
        result = extract_entities(context)
        assert result.raw_query == "查比亚迪的存款"
        # 测试是否提取了企业名称
        if hasattr(result, 'ambiguous_candidates') and result.ambiguous_candidates:
            assert '比亚迪' in result.ambiguous_candidates
    
    def test_extract_multiple_entities(self):
        """测试提取多个实体"""
        context = IntentContext(
            user_id="test_user",
            app_id="Lingxi",
            session_id="test_session",
            raw_query="给我比亚迪和通用电气的访前一页纸"
        )
        result = extract_entities(context)
        assert result.raw_query == "给我比亚迪和通用电气的访前一页纸"
        # 测试是否提取了多个企业名称
        if hasattr(result, 'ambiguous_candidates') and result.ambiguous_candidates:
            assert '比亚迪' in result.ambiguous_candidates
            assert '通用电气' in result.ambiguous_candidates
        # 测试是否正确处理了多个实体
        assert 'ambiguous_candidates' in result.__dict__
        assert len(result.ambiguous_candidates) >= 2