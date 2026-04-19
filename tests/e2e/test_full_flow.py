import pytest
import requests

class TestFullFlow:
    def test_deposit_query_full_flow(self, base_url, test_user_id, test_session_id, test_app_id, test_company):
        """测试存款查询完整流程"""
        # 1. 调用意图引擎
        intent_url = f"{base_url}/intent/recognize"
        intent_data = {
            "user_id": test_user_id,
            "app_id": test_app_id,
            "session_id": test_session_id,
            "raw_query": f"查{test_company}的存款"
        }
        intent_response = requests.post(intent_url, json=intent_data)
        assert intent_response.status_code == 200
        intent_result = intent_response.json()
        
        # 2. 检查意图引擎返回结果
        assert "action_suggestion" in intent_result
        assert intent_result["action_suggestion"]["action"] == "EXECUTE"
        assert intent_result["action_suggestion"]["skill"] == "SKILL_DEPOSIT_QUERY_V1"
        
        # 3. 提取参数并调用存款查询API
        parameters = intent_result["action_suggestion"]["parameters"]
        company_name = parameters.get("company_name") or parameters.get("target_company")
        assert company_name is not None
        
        deposit_url = f"{base_url}/api/deposit/query"
        deposit_data = {"company_name": company_name}
        deposit_response = requests.post(deposit_url, json=deposit_data)
        assert deposit_response.status_code == 200
        deposit_result = deposit_response.json()
        assert deposit_result["code"] == 200
        assert "deposit_info" in deposit_result["data"]
    
    def test_loan_query_full_flow(self, base_url, test_user_id, test_session_id, test_app_id, test_company):
        """测试贷款查询完整流程"""
        # 1. 调用意图引擎
        intent_url = f"{base_url}/intent/recognize"
        intent_data = {
            "user_id": test_user_id,
            "app_id": test_app_id,
            "session_id": test_session_id,
            "raw_query": f"查{test_company}的贷款"
        }
        intent_response = requests.post(intent_url, json=intent_data)
        assert intent_response.status_code == 200
        intent_result = intent_response.json()
        
        # 2. 检查意图引擎返回结果
        assert "action_suggestion" in intent_result
        assert intent_result["action_suggestion"]["action"] == "EXECUTE"
        assert intent_result["action_suggestion"]["skill"] == "SKILL_LOAN_QUERY_V1"
        
        # 3. 提取参数并调用贷款查询API
        parameters = intent_result["action_suggestion"]["parameters"]
        company_name = parameters.get("company_name") or parameters.get("target_company")
        assert company_name is not None
        
        loan_url = f"{base_url}/api/loan/query"
        loan_data = {"company_name": company_name}
        loan_response = requests.post(loan_url, json=loan_data)
        assert loan_response.status_code == 200
        loan_result = loan_response.json()
        assert loan_result["code"] == 200
        assert "loan_info" in loan_result["data"]
    
    def test_visit_report_full_flow(self, base_url, test_user_id, test_session_id, test_app_id, test_company):
        """测试访前一页纸下载完整流程"""
        # 1. 调用意图引擎
        intent_url = f"{base_url}/intent/recognize"
        intent_data = {
            "user_id": test_user_id,
            "app_id": test_app_id,
            "session_id": test_session_id,
            "raw_query": f"获取{test_company}的访前一页纸"
        }
        intent_response = requests.post(intent_url, json=intent_data)
        assert intent_response.status_code == 200
        intent_result = intent_response.json()
        
        # 2. 检查意图引擎返回结果
        assert "action_suggestion" in intent_result
        assert intent_result["action_suggestion"]["action"] == "EXECUTE"
        assert intent_result["action_suggestion"]["skill"] == "SKILL_VISIT_REPORT_V1"
        
        # 3. 提取参数并调用访前一页纸下载API
        parameters = intent_result["action_suggestion"]["parameters"]
        company_name = parameters.get("company_name") or parameters.get("target_company")
        assert company_name is not None
        
        visit_report_url = f"{base_url}/api/visit-report/download"
        visit_report_data = {"company_name": company_name}
        visit_report_response = requests.post(visit_report_url, json=visit_report_data)
        assert visit_report_response.status_code == 200
        # 检查响应是否为文件下载
        assert "Content-Disposition" in visit_report_response.headers
        assert "attachment" in visit_report_response.headers["Content-Disposition"]