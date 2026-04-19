import pytest
import requests

class TestAPIIntegration:
    def test_deposit_api_integration(self, base_url, test_company):
        """测试存款查询API集成"""
        # 模拟灵犀前端调用存款查询API
        url = f"{base_url}/api/deposit/query"
        data = {"company_name": test_company}
        response = requests.post(url, json=data)
        assert response.status_code == 200
        result = response.json()
        assert result["code"] == 200
        assert result["data"]["company_name"] == test_company
        assert "deposit_info" in result["data"]
    
    def test_loan_api_integration(self, base_url, test_company):
        """测试贷款查询API集成"""
        # 模拟灵犀前端调用贷款查询API
        url = f"{base_url}/api/loan/query"
        data = {"company_name": test_company}
        response = requests.post(url, json=data)
        assert response.status_code == 200
        result = response.json()
        assert result["code"] == 200
        assert result["data"]["company_name"] == test_company
        assert "loan_info" in result["data"]
    
    def test_visit_report_api_integration(self, base_url, test_company):
        """测试访前一页纸下载API集成"""
        # 模拟灵犀前端调用访前一页纸下载API
        url = f"{base_url}/api/visit-report/download"
        data = {"company_name": test_company}
        response = requests.post(url, json=data)
        assert response.status_code == 200
        # 检查响应是否为文件下载
        assert "Content-Disposition" in response.headers
        assert "attachment" in response.headers["Content-Disposition"]