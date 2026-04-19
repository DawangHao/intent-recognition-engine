from fastapi import APIRouter
import csv
import os
from backend.config import config

router = APIRouter()


@router.get("/api/companies")
async def get_companies(keyword: str = ""):
    """企业列表接口"""
    companies = []
    
    # 优先使用 企业信息.csv
    company_csv_path = os.path.join(config.DATA_DIR, '企业信息.csv')
    if os.path.exists(company_csv_path):
        with open(company_csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                company_name = row.get('企业名称', '')
                if keyword in company_name:
                    companies.append({
                        'id': row.get('企业ID', ''),
                        'name': company_name
                    })
    else:
        # 回退到 bank_customers.csv
        with open(config.CUSTOMERS_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                full_name = row.get('customer_full_name', '')
                short_name = row.get('customer_short_name', '')
                if keyword in full_name or keyword in short_name:
                    companies.append({
                        'id': row.get('customer_id', ''),
                        'name': full_name
                    })
    
    # 限制返回数量
    return companies[:10]
