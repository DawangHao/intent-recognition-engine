from fastapi import APIRouter
from fastapi.responses import FileResponse
import os
import urllib.parse
from backend.config import config

router = APIRouter()


@router.post("/api/visit-report/download")
async def download_visit_report(data: dict):
    """访前一页纸下载接口"""
    company_name = data.get('company_name', '') or data.get('enterprise_name', '')
    if not company_name:
        return {"code": 400, "message": "企业名称不能为空"}
    
    # 构建文件路径
    file_name = f"{company_name}.docx"
    file_path = os.path.join(config.DATA_DIR, '访前一页纸', file_name)
    
    if not os.path.exists(file_path):
        # 尝试查找近似匹配
        files = os.listdir(os.path.join(config.DATA_DIR, '访前一页纸'))
        for f in files:
            if company_name in f:
                file_path = os.path.join(config.DATA_DIR, '访前一页纸', f)
                file_name = f
                break
        else:
            return {"code": 404, "message": "未找到该企业的访前一页纸"}
    
    # 设置正确的Content-Disposition头
    encoded_filename = urllib.parse.quote(file_name)
    headers = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
    }
    
    return FileResponse(
        path=file_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers
    )
