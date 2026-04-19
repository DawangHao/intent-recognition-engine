import pytest
import requests

class TestApiCompanies:
    """企业列表接口测试"""
    
    def test_companies_with_keyword(self, base_url):
        """测试使用关键词查询企业列表"""
        response = requests.get(f"{base_url}/api/companies?keyword=比亚迪")
        assert response.status_code == 200
        result = response.json()
        assert result["code"] == 200
        assert isinstance(result["data"], list)
    
    def test_companies_without_keyword(self, base_url):
        """测试不使用关键词查询企业列表"""
        response = requests.get(f"{base_url}/api/companies")
        assert response.status_code == 200
        result = response.json()
        assert result["code"] == 200
        assert isinstance(result["data"], list)
