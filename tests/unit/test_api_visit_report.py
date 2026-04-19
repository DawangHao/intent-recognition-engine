import pytest
import requests

class TestVisitReportAPI:
    def test_download_visit_report(self, base_url, test_company):
        """测试访前一页纸下载接口"""
        url = f"{base_url}/api/visit-report/download"
        data = {"company_name": test_company}
        response = requests.post(url, json=data)
        # 检查响应状态码
        assert response.status_code == 200
        # 检查响应头
        assert "Content-Disposition" in response.headers
        assert "Content-Type" in response.headers
        assert response.headers["Content-Type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    
    def test_download_visit_report_without_company(self, base_url):
        """测试访前一页纸下载接口（缺少企业名称）"""
        url = f"{base_url}/api/visit-report/download"
        data = {}
        response = requests.post(url, json=data)
        assert response.status_code == 200
        result = response.json()
        assert result["code"] == 400
        assert result["message"] == "企业名称不能为空"
    
    def test_download_visit_report_not_found(self, base_url):
        """测试访前一页纸下载接口（企业不存在）"""
        url = f"{base_url}/api/visit-report/download"
        data = {"company_name": "不存在的企业"}
        response = requests.post(url, json=data)
        assert response.status_code == 200
        result = response.json()
        assert result["code"] == 404
        assert result["message"] == "未找到该企业的访前一页纸"