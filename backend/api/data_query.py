import csv
import os
from fastapi import APIRouter

router = APIRouter()

# 获取CSV文件路径
CSV_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', '企业信息.csv')


@router.post("/api/deposit/query")
async def query_deposit(data: dict):
    """存款查询接口"""
    company_name = data.get('company_name', '') or data.get('enterprise_name', '')
    if not company_name:
        return {"code": 400, "message": "企业名称不能为空"}
    
    # 从CSV文件中查询数据
    try:
        with open(CSV_FILE_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['企业名称'] == company_name:
                    return {
                        "code": 200,
                        "data": {
                            "company_name": company_name,
                            "deposit_info": {
                                "存款时点(元)": float(row['存款时点(元)']),
                                "存款年日均(元)": float(row['存款年日均(元)']),
                                "存款FTP净利润(元)": float(row['存款FTP净利润(元)']),
                                "预测所有银行存款金额(元)": float(row['预测所有银行存款金额(元)'])
                            }
                        }
                    }
        # 未找到企业
        return {"code": 404, "message": f"未找到企业: {company_name}"}
    except Exception as e:
        return {"code": 500, "message": f"查询失败: {str(e)}"}


@router.post("/api/loan/query")
async def query_loan(data: dict):
    """贷款查询接口"""
    company_name = data.get('company_name', '') or data.get('enterprise_name', '')
    if not company_name:
        return {"code": 400, "message": "企业名称不能为空"}
    
    # 从CSV文件中查询数据
    try:
        with open(CSV_FILE_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['企业名称'] == company_name:
                    return {
                        "code": 200,
                        "data": {
                            "company_name": company_name,
                            "loan_info": {
                                "授信额度(元)": float(row['授信额度（元）']),
                                "贷款时点(元)": float(row['贷款时点（元）']),
                                "贷款FTP净利润(元)": float(row['贷款FTP净利润(元)']),
                                "预测所有银行贷款金额(元)": float(row['预测所有银行贷款金额(元)'])
                            }
                        }
                    }
        # 未找到企业
        return {"code": 404, "message": f"未找到企业: {company_name}"}
    except Exception as e:
        return {"code": 500, "message": f"查询失败: {str(e)}"}


@router.post("/api/settlement/query")
async def query_settlement(data: dict):
    """企业结算分查询接口"""
    company_name = data.get('company_name', '') or data.get('enterprise_name', '')
    if not company_name:
        return {"code": 400, "message": "企业名称不能为空"}
    
    # 从CSV文件中查询数据
    try:
        with open(CSV_FILE_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['企业名称'] == company_name:
                    # 使用资质分作为结算分
                    settlement_score = float(row['资质分']) if row['资质分'] else 0.0
                    return {
                        "code": 200,
                        "data": {
                            "company_name": company_name,
                            "settlement_info": {
                                "结算分": settlement_score,
                                "我行结算金额(元)": float(row['我行结算金额(元)']),
                                "预测所有银行结算金额(元)": float(row['预测所有银行结算金额(元)'])
                            }
                        }
                    }
        # 未找到企业
        return {"code": 404, "message": f"未找到企业: {company_name}"}
    except Exception as e:
        return {"code": 500, "message": f"查询失败: {str(e)}"}


@router.get("/api/recommend/companies")
async def recommend_companies():
    """好客推荐接口，返回5个好企业"""
    try:
        # 模拟推荐数据
        recommended_companies = [
            {
                "company_name": "江苏银行铁路集团",
                "registered_capital": "10000万",
                "establishment_date": "2023-12-23",
                "address": "南京经济技术开发区兴智路6号兴智科技园B座",
                "tags": ["存研所注册企业", "朋友圈"],
                "reasons": [
                    "存研企业 [南京银行股份有限公司] 于2024年12月4日成立子公司 [江苏银行铁路集团]",
                    "可通过xxx企业介绍 (三星)"
                ]
            },
            {
                "company_name": "南京科技创新有限公司",
                "registered_capital": "15500万",
                "establishment_date": "2024-01-15",
                "address": "南京市玄武区科技创新园A座1001室",
                "tags": ["存研所注册企业", "朋友圈"],
                "reasons": [
                    "存研企业 [南京科技发展有限公司] 于2024年1月15日成立子公司 [南京科技创新有限公司",
                    "可通过南京科技发展有限公司介绍 (四星)"
                ]
            },
            {
                "company_name": "江苏智能制造有限公司",
                "registered_capital": "30000万",
                "establishment_date": "2023-11-05",
                "address": "常州市武进区智能制造产业园",
                "tags": ["存研所注册企业", "朋友圈"],
                "reasons": [
                    "存研企业 [江苏制造产业集团有限公司] 于2023年11月5日成立子公司 [江苏智能制造有限公司",
                    "可通过江苏制造产业集团有限公司介绍 (五星)"
                ]
            },
            {
                "company_name": "上海数字科技有限公司",
                "registered_capital": "25000万",
                "establishment_date": "2024-02-10",
                "address": "上海市浦东新区张江高科技园区",
                "tags": ["存研所注册企业"],
                "reasons": [
                    "存研企业 [上海科技集团有限公司] 于2024年2月10日成立子公司 [上海数字科技有限公司",
                    "可通过上海科技集团有限公司介绍 (四星)"
                ]
            },
            {
                "company_name": "浙江绿色能源有限公司",
                "registered_capital": "40000万",
                "establishment_date": "2023-09-18",
                "address": "杭州市西湖区绿色能源产业园",
                "tags": ["朋友圈"],
                "reasons": [
                    "可通过浙江能源集团有限公司介绍 (五星)",
                    "新能源行业优质企业"
                ]
            }
        ]
        
        return {
            "code": 200,
            "data": {
                "recommended_companies": recommended_companies
            }
        }
    except Exception as e:
        return {"code": 500, "message": f"推荐失败: {str(e)}"}


@router.post("/api/customer/card")
async def query_customer_card(data: dict):
    """客户卡片查询接口"""
    company_name = data.get('company_name', '') or data.get('enterprise_name', '')
    if not company_name:
        return {"code": 400, "message": "企业名称不能为空"}
    
    try:
        with open(CSV_FILE_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['企业名称'] == company_name:
                    # 生成标签列表
                    tags = []
                    # 从企业类型、行业等信息生成标签
                    if row.get('企业类型'):
                        tags.append(row['企业类型'])
                    if row.get('企查查行业门类'):
                        tags.append(row['企查查行业门类'])
                    if row.get('价值客户标志') == '是':
                        tags.append('重点客户')
                    if row.get('授信客户标志') == '是':
                        tags.append('战略合作伙伴')
                    
                    # 构建客户卡片数据
                    return {
                        "code": 200,
                        "data": {
                            "company_name": company_name,
                            "company_short": row.get('企业简称', ''),
                            "tags": tags,
                            "manager": row.get('管户人', ''),
                            "organization": row.get('我行政府类客户标志', ''),
                            "registered_capital": row.get('注册资本', ''),
                            "establishment_date": row.get('成立日期', ''),
                            "address": row.get('通信地址', ''),
                            "quick_actions": [
                                {
                                    "name": "查存款",
                                    "skill_id": "SKILL_DEPOSIT_QUERY_V1"
                                },
                                {
                                    "name": "查贷款",
                                    "skill_id": "SKILL_LOAN_QUERY_V1"
                                },
                                {
                                    "name": "查结算",
                                    "skill_id": "SKILL_SETTLEMENT_QUERY_V1"
                                },
                                {
                                    "name": "访前一页纸",
                                    "skill_id": "SKILL_VISIT_REPORT_V1"
                                }
                            ]
                        }
                    }
        return {"code": 404, "message": f"未找到企业: {company_name}"}
    except Exception as e:
        return {"code": 500, "message": f"查询失败: {str(e)}"}
