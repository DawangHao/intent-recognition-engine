import pytest
import requests

class TestDataQueryAPI:
    def test_query_deposit(self, base_url, test_company):
        """测试存款查询接口"""
        url = f"{base_url}/api/deposit/query"
        data = {"company_name": test_company}
        response = requests.post(url, json=data)
        assert response.status_code == 200
        result = response.json()
        assert result["code"] == 200
        assert "data" in result
        assert "deposit_info" in result["data"]
    
    def test_query_loan(self, base_url, test_company):
        """测试贷款查询接口"""
        url = f"{base_url}/api/loan/query"
        data = {"company_name": test_company}
        response = requests.post(url, json=data)
        assert response.status_code == 200
        result = response.json()
        assert result["code"] == 200
        assert "data" in result
        assert "loan_info" in result["data"]
    
    def test_query_deposit_without_company(self, base_url):
        """测试存款查询接口（缺少企业名称）"""
        url = f"{base_url}/api/deposit/query"
        data = {}
        response = requests.post(url, json=data)
        assert response.status_code == 200
        result = response.json()
        assert result["code"] == 400
        assert result["message"] == "企业名称不能为空"
    
    def test_query_loan_without_company(self, base_url):
        """测试贷款查询接口（缺少企业名称）"""
        url = f"{base_url}/api/loan/query"
        data = {}
        response = requests.post(url, json=data)
        assert response.status_code == 200
        result = response.json()
        assert result["code"] == 400
        assert result["message"] == "企业名称不能为空"