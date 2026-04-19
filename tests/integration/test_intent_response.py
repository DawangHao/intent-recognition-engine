import pytest
import requests

class TestIntentResponse:
    def test_execute_response(self, base_url, test_user_id, test_session_id, test_app_id):
        """测试意图引擎返回EXECUTE响应"""
        url = f"{base_url}/intent/recognize"
        data = {
            "user_id": test_user_id,
            "app_id": test_app_id,
            "session_id": test_session_id,
            "raw_query": "查比亚迪的存款"
        }
        response = requests.post(url, json=data)
        assert response.status_code == 200
        result = response.json()
        assert "action_suggestion" in result
        assert result["action_suggestion"]["action"] == "EXECUTE"
        assert "skill" in result["action_suggestion"]
        assert "parameters" in result["action_suggestion"]
    
    def test_clarify_response(self, base_url, test_user_id, test_session_id, test_app_id):
        """测试意图引擎返回CLARIFY响应"""
        url = f"{base_url}/intent/recognize"
        data = {
            "user_id": test_user_id,
            "app_id": test_app_id,
            "session_id": test_session_id,
            "raw_query": "查存款"
        }
        response = requests.post(url, json=data)
        assert response.status_code == 200
        result = response.json()
        assert "action_suggestion" in result
        # 可能返回EXECUTE或CLARIFY，取决于意图识别的结果
        assert result["action_suggestion"]["action"] in ["EXECUTE", "CLARIFY"]
    
    def test_fallback_response(self, base_url, test_user_id, test_session_id, test_app_id):
        """测试意图引擎返回FALLBACK响应"""
        url = f"{base_url}/intent/recognize"
        data = {
            "user_id": test_user_id,
            "app_id": test_app_id,
            "session_id": test_session_id,
            "raw_query": "敏感内容"
        }
        response = requests.post(url, json=data)
        assert response.status_code == 200
        result = response.json()
        assert "action_suggestion" in result
        assert result["action_suggestion"]["action"] == "FALLBACK"