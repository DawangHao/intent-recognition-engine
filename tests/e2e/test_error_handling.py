import pytest
import requests

class TestErrorHandling:
    def test_empty_query(self, base_url, test_user_id, test_session_id, test_app_id):
        """测试空查询处理"""
        intent_url = f"{base_url}/intent/recognize"
        intent_data = {
            "user_id": test_user_id,
            "app_id": test_app_id,
            "session_id": test_session_id,
            "raw_query": ""
        }
        intent_response = requests.post(intent_url, json=intent_data)
        assert intent_response.status_code == 200
        intent_result = intent_response.json()
        assert "action_suggestion" in intent_result
    
    def test_invalid_company(self, base_url, test_user_id, test_session_id, test_app_id):
        """测试无效企业名称处理"""
        intent_url = f"{base_url}/intent/recognize"
        intent_data = {
            "user_id": test_user_id,
            "app_id": test_app_id,
            "session_id": test_session_id,
            "raw_query": "查不存在的企业的存款"
        }
        intent_response = requests.post(intent_url, json=intent_data)
        assert intent_response.status_code == 200
        intent_result = intent_response.json()
        assert "action_suggestion" in intent_result
        
        # 尝试调用API
        if intent_result["action_suggestion"]["action"] == "EXECUTE":
            parameters = intent_result["action_suggestion"]["parameters"]
            company_name = parameters.get("company_name") or parameters.get("target_company")
            if company_name:
                deposit_url = f"{base_url}/api/deposit/query"
                deposit_data = {"company_name": company_name}
                deposit_response = requests.post(deposit_url, json=deposit_data)
                assert deposit_response.status_code == 200
    
    def test_api_error_handling(self, base_url):
        """测试API错误处理"""
        # 测试存款查询API（缺少参数）
        deposit_url = f"{base_url}/api/deposit/query"
        deposit_data = {}
        deposit_response = requests.post(deposit_url, json=deposit_data)
        assert deposit_response.status_code == 200
        deposit_result = deposit_response.json()
        assert deposit_result["code"] == 400
        
        # 测试贷款查询API（缺少参数）
        loan_url = f"{base_url}/api/loan/query"
        loan_data = {}
        loan_response = requests.post(loan_url, json=loan_data)
        assert loan_response.status_code == 200
        loan_result = loan_response.json()
        assert loan_result["code"] == 400
        
        # 测试访前一页纸下载API（缺少参数）
        visit_report_url = f"{base_url}/api/visit-report/download"
        visit_report_data = {}
        visit_report_response = requests.post(visit_report_url, json=visit_report_data)
        assert visit_report_response.status_code == 200
        visit_report_result = visit_report_response.json()
        assert visit_report_result["code"] == 400