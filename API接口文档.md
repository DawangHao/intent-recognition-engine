# 银行意图识别引擎 API 文档

## 1. 文档概览

本文档描述了银行意图识别引擎的所有API接口，包括意图识别、健康检查、企业列表查询、存款查询、贷款查询和访前一页纸下载等功能。

### 1.1 基本信息

- **服务地址**：`http://localhost:8000`
- **API版本**：v1.0
- **请求格式**：JSON
- **响应格式**：JSON
- **认证方式**：无（开发环境）

## 2. 接口列表

| 接口路径 | 方法 | 功能描述 |
| :--- | :--- | :--- |
| `/intent/recognize` | POST | 意图识别接口 |
| `/health` | GET | 健康检查接口 |
| `/api/companies` | GET | 企业列表接口 |
| `/api/deposit/query` | POST | 存款查询接口 |
| `/api/loan/query` | POST | 贷款查询接口 |
| `/api/settlement/query` | POST | 企业结算分查询接口 |
| `/api/recommend/companies` | GET | 好客推荐接口 |
| `/api/visit-report/download` | POST | 访前一页纸下载接口 |
| `/api/customer/card` | POST | 客户卡片查询接口 |
| `/lingxi_ui` | GET | 静态文件服务 |

## 3. 详细接口说明

### 3.1 意图识别接口

**接口路径**：`/intent/recognize`

**请求方法**：POST

**功能描述**：接收用户查询，识别用户意图并返回处理结果

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
| :--- | :--- | :--- | :--- |
| `user_id` | string | 是 | 用户ID |
| `app_id` | string | 是 | 应用ID (lingxi, guangnian) |
| `session_id` | string | 是 | 会话ID |
| `raw_query` | string | 是 | 用户原始查询 |
| `normalized_query` | string | 否 | 规范化后的查询 |
| `final_query` | string | 否 | 最终查询 |
| `intent_id` | string | 否 | 意图ID |
| `confidence` | number | 否 | 置信度 |
| `slots_state` | object | 否 | 槽位状态 |
| `is_rejected` | boolean | 否 | 是否被拒绝 |
| `rejection_reason` | string | 否 | 拒绝原因 |
| `ambiguous_candidates` | object | 否 | 歧义候选 |
| `missing_slots` | array | 否 | 缺失槽位 |
| `action` | string | 否 | 操作类型 |
| `response_text` | string | 否 | 响应文本 |
| `action_suggestion` | object | 否 | 操作建议 |
| `llm_raw_response` | object | 否 | 大模型原始响应 |
| `prompt` | string | 否 | 发送给大模型的提示词 |
| `history_context` | array | 否 | 历史上下文 |
| `last_turn_query` | string | 否 | 上一轮查询 |
| `step1_duration` | number | 否 | 步骤1耗时（毫秒） |
| `step2_duration` | number | 否 | 步骤2耗时（毫秒） |
| `step3_duration` | number | 否 | 步骤3耗时（毫秒） |
| `step4_duration` | number | 否 | 步骤4耗时（毫秒） |
| `step5_duration` | number | 否 | 步骤5耗时（毫秒） |
| `total_duration` | number | 否 | 总耗时（毫秒） |

**响应格式**：

```json
{
  "user_id": "test_user_001",
  "app_id": "lingxi",
  "session_id": "session_001",
  "raw_query": "查比亚迪的存款",
  "normalized_query": "查<AMBIGUOUS_ENTITY key=\"比亚迪\"/>的存款\n（1）无锡比亚迪科技有限公司\n（2）常州比亚迪电池技术有限公司\n（3）南京比亚迪半导体研究所",
  "final_query": null,
  "intent_id": "SKILL_DEPOSIT_QUERY_V1",
  "confidence": 0.95,
  "slots_state": {
    "target_company": "无锡比亚迪科技有限公司"
  },
  "is_rejected": false,
  "rejection_reason": null,
  "ambiguous_candidates": {
    "比亚迪": [
      {
        "id": "",
        "name": "无锡比亚迪科技有限公司"
      },
      {
        "id": "",
        "name": "常州比亚迪电池技术有限公司"
      },
      {
        "id": "",
        "name": "南京比亚迪半导体研究所"
      }
    ]
  },
  "missing_slots": [],
  "action": "EXECUTE",
  "response_text": "查询无锡比亚迪科技有限公司的存款",
  "action_suggestion": {
    "action": "EXECUTE",
    "skill": "SKILL_DEPOSIT_QUERY_V1",
    "parameters": {
      "target_company": "无锡比亚迪科技有限公司"
    }
  },
  "llm_raw_response": {
    "action": "EXECUTE",
    "skill": "SKILL_DEPOSIT_QUERY_V1",
    "parameters": {
      "target_company": "无锡比亚迪科技有限公司"
    }
  },
  "prompt": "...",
  "history_context": [
    {
      "user": "你好",
      "agent": "您好，有什么可以帮助您的？",
      "timestamp": "10:30:45"
    }
  ],
  "last_turn_query": "你好",
  "step1_duration": 10,
  "step2_duration": 15,
  "step3_duration": 20,
  "step4_duration": 2500,
  "step5_duration": 5,
  "total_duration": 2550
}
```

### 3.2 健康检查接口

**接口路径**：`/health`

**请求方法**：GET

**功能描述**：检查服务健康状态

**请求参数**：无

**响应格式**：

```json
{
  "status": "healthy",
  "app_name": "银行意图识别引擎",
  "version": "1.0.0"
}
```

### 3.3 企业列表接口

**接口路径**：`/api/companies`

**请求方法**：GET

**功能描述**：根据关键词查询企业列表

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
| :--- | :--- | :--- | :--- |
| `keyword` | string | 否 | 搜索关键词 |

**响应格式**：

```json
[
  {
    "id": "C001",
    "name": "无锡比亚迪科技有限公司"
  },
  {
    "id": "C002",
    "name": "常州比亚迪电池技术有限公司"
  }
]
```

### 3.4 存款查询接口

**接口路径**：`/api/deposit/query`

**请求方法**：POST

**功能描述**：查询企业存款信息

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
| :--- | :--- | :--- | :--- |
| `company_name` | string | 否 | 企业名称 |
| `enterprise_name` | string | 否 | 企业名称（兼容字段） |

**请求示例**：

```json
{
  "company_name": "无锡比亚迪科技有限公司"
}
```

```json
{
  "enterprise_name": "无锡比亚迪科技有限公司"
}
```

**响应格式**：

```json
{
  "code": 200,
  "data": {
    "company_name": "无锡比亚迪科技有限公司",
    "deposit_info": {
      "存款时点(元)": 123456789.12,
      "存款年日均(元)": 987654321.34,
      "存款FTP净利润(元)": 5678901.23,
      "预测所有银行存款金额(元)": 234567890.56
    }
  }
}
```

**错误响应**：

```json
{
  "code": 400,
  "message": "企业名称不能为空"
}
```

### 3.5 贷款查询接口

**接口路径**：`/api/loan/query`

**请求方法**：POST

**功能描述**：查询企业贷款信息

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
| :--- | :--- | :--- | :--- |
| `company_name` | string | 否 | 企业名称 |
| `enterprise_name` | string | 否 | 企业名称（兼容字段） |

**请求示例**：

```json
{
  "company_name": "无锡比亚迪科技有限公司"
}
```

```json
{
  "enterprise_name": "无锡比亚迪科技有限公司"
}
```

**响应格式**：

```json
{
  "code": 200,
  "data": {
    "company_name": "无锡比亚迪科技有限公司",
    "loan_info": {
      "授信额度(元)": 500000000.00,
      "贷款时点(元)": 250000000.00,
      "贷款FTP净利润(元)": 12500000.00,
      "预测所有银行贷款金额(元)": 300000000.00
    }
  }
}
```

**错误响应**：

```json
{
  "code": 400,
  "message": "企业名称不能为空"
}
```

### 3.6 企业结算分查询接口

**接口路径**：`/api/settlement/query`

**请求方法**：POST

**功能描述**：查询企业结算分信息

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
| :--- | :--- | :--- | :--- |
| `company_name` | string | 否 | 企业名称 |
| `enterprise_name` | string | 否 | 企业名称（兼容字段） |

**请求示例**：

```json
{
  "company_name": "无锡比亚迪科技有限公司"
}
```

```json
{
  "enterprise_name": "无锡比亚迪科技有限公司"
}
```

**响应格式**：

```json
{
  "code": 200,
  "data": {
    "company_name": "无锡比亚迪科技有限公司",
    "settlement_info": {
      "结算分": 85.5,
      "我行结算金额(元)": 123456789.12,
      "预测所有银行结算金额(元)": 234567890.56
    }
  }
}
```

**错误响应**：

```json
{
  "code": 400,
  "message": "企业名称不能为空"
}
```

### 3.7 访前一页纸下载接口

**接口路径**：`/api/visit-report/download`

**请求方法**：POST

**功能描述**：下载企业访前一页纸文档

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
| :--- | :--- | :--- | :--- |
| `company_name` | string | 否 | 企业名称 |
| `enterprise_name` | string | 否 | 企业名称（兼容字段） |

**请求示例**：

```json
{
  "company_name": "无锡比亚迪科技有限公司"
}
```

```json
{
  "enterprise_name": "无锡比亚迪科技有限公司"
}
```

**响应格式**：
- 成功：返回 DOCX 文件下载
- 失败：返回错误信息

**错误响应**：

```json
{
  "code": 400,
  "message": "企业名称不能为空"
}
```

```json
{
  "code": 404,
  "message": "未找到该企业的访前一页纸"
}
```

### 3.7 好客推荐接口

**接口路径**：`/api/recommend/companies`

**请求方法**：GET

**功能描述**：返回5个推荐的优质企业信息

**请求参数**：无

**响应格式**：

```json
{
  "code": 200,
  "data": {
    "recommended_companies": [
      {
        "company_name": "江苏银行铁路集团",
        "registered_capital": "10000万",
        "establishment_date": "2023-12-23",
        "address": "南京经济技术开发区兴智路6号兴智科技园B栋",
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
          "存研企业 [南京科技发展有限公司] 于2024年1月15日成立子公司 [南京科技创新有限公司]",
          "可通过南京科技发展有限公司介绍 (四星)"
        ]
      }
    ]
  }
}
```

**错误响应**：

```json
{
  "code": 500,
  "message": "推荐失败: [错误信息]"
}
```

### 3.8 客户卡片查询接口

**接口路径**：`/api/customer/card`

**请求方法**：POST

**功能描述**：查询企业客户卡片信息，包含企业基本信息、标签和快速操作入口

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
| :--- | :--- | :--- | :--- |
| `company_name` | string | 否 | 企业名称 |
| `enterprise_name` | string | 否 | 企业名称（兼容字段） |

**请求示例**：

```json
{
  "company_name": "南京通用电气有限公司"
}
```

**响应格式**：

```json
{
  "code": 200,
  "data": {
    "company_name": "南京通用电气有限公司",
    "company_short": "通用电气",
    "tags": ["非授信_小型", "信息技术", "重点客户", "战略合作伙伴"],
    "manager": "陆尧",
    "organization": "",
    "registered_capital": "784.8172万元",
    "establishment_date": "2016-03-28",
    "address": "",
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
```

**错误响应**：

```json
{
  "code": 400,
  "message": "企业名称不能为空"
}
```

```json
{
  "code": 404,
  "message": "未找到企业: 南京通用电气有限公司"
}
```

### 3.9 静态文件服务

**接口路径**：`/lingxi_ui`

**请求方法**：GET

**功能描述**：提供前端页面访问

**请求参数**：无

**响应格式**：HTML页面

## 4. 错误处理

### 4.1 通用错误响应

| 状态码 | 描述 |
| :--- | :--- |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 4.2 业务错误响应

| 错误码 | 描述 |
| :--- | :--- |
| 400 | 企业名称不能为空 |
| 404 | 未找到该企业的访前一页纸 |

## 5. 附录

### 5.1 数据结构定义

#### 5.1.1 意图上下文 (IntentContext)

| 字段名 | 类型 | 描述 |
| :--- | :--- | :--- |
| `user_id` | string | 用户ID |
| `app_id` | string | 应用ID |
| `session_id` | string | 会话ID |
| `raw_query` | string | 用户原始查询 |
| `normalized_query` | string | 规范化后的查询 |
| `final_query` | string | 最终查询 |
| `intent_id` | string | 意图ID |
| `confidence` | number | 置信度 |
| `slots_state` | object | 槽位状态 |
| `is_rejected` | boolean | 是否被拒绝 |
| `rejection_reason` | string | 拒绝原因 |
| `ambiguous_candidates` | object | 歧义候选 |
| `missing_slots` | array | 缺失槽位 |
| `action` | string | 操作类型 |
| `response_text` | string | 响应文本 |
| `action_suggestion` | object | 操作建议 |
| `llm_raw_response` | object | 大模型原始响应 |
| `prompt` | string | 发送给大模型的提示词 |
| `history_context` | array | 历史上下文 |
| `last_turn_query` | string | 上一轮查询 |
| `step1_duration` | number | 步骤1耗时（毫秒） |
| `step2_duration` | number | 步骤2耗时（毫秒） |
| `step3_duration` | number | 步骤3耗时（毫秒） |
| `step4_duration` | number | 步骤4耗时（毫秒） |
| `step5_duration` | number | 步骤5耗时（毫秒） |
| `total_duration` | number | 总耗时（毫秒） |

### 5.2 技能列表

| 技能ID | 技能名称 | API端点 |
| :--- | :--- | :--- |
| `SKILL_DEPOSIT_QUERY_V1` | 查询企业的本外币合计对公存款余额 | `/api/deposit/query` |
| `SKILL_LOAN_QUERY_V1` | 查询企业的贷款信息 | `/api/loan/query` |
| `SKILL_SETTLEMENT_QUERY_V1` | 查询企业结算分 | `/api/settlement/query` |
| `SKILL_VISIT_REPORT_V1` | 下载企业访前一页纸 | `/api/visit-report/download` |
| `SKILL_COMPANY_RECOMMEND_V1` | 好客推荐 | `/api/recommend/companies` |
| `SKILL_CUSTOMER_CARD_V1` | 客户卡片 | `/api/customer/card` |

## 6. 接口调用示例

### 6.1 意图识别接口调用

```bash
curl -X POST http://localhost:8000/intent/recognize \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_001",
    "app_id": "lingxi",
    "session_id": "session_001",
    "raw_query": "查比亚迪的存款"
  }'
```

### 6.2 企业列表接口调用

```bash
curl -X GET "http://localhost:8000/api/companies?keyword=比亚迪"
```

### 6.3 存款查询接口调用

```bash
curl -X POST http://localhost:8000/api/deposit/query \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "无锡比亚迪科技有限公司"
  }'
```

### 6.4 贷款查询接口调用

```bash
curl -X POST http://localhost:8000/api/loan/query \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "无锡比亚迪科技有限公司"
  }'
```

### 6.5 访前一页纸下载接口调用

```bash
curl -X POST http://localhost:8000/api/visit-report/download \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "无锡比亚迪科技有限公司"
  }' \
  -o "无锡比亚迪科技有限公司.docx"
```

## 7. 注意事项

1. 所有接口均在开发环境下运行，生产环境需添加认证和授权机制
2. 静态文件服务仅用于前端调试，生产环境应使用专业的静态文件服务器
3. 业务API接口返回的数据为模拟数据，实际使用时需对接真实的业务系统
4. 大模型调用可能会有一定的延迟，建议在前端添加加载状态提示
5. 意图识别接口的响应时间主要取决于大模型的处理速度

## 8. 版本历史

| 版本 | 日期 | 变更内容 |
| :--- | :--- | :--- |
| v1.0.3 | 2026-04-19 | 新增客户卡片技能，添加/api/customer/card接口 |
| v1.0.2 | 2026-04-18 | 新增好客推荐技能，添加/api/recommend/companies接口 |
| v1.0.1 | 2026-04-07 | 增加对enterprise_name字段的支持，提高接口兼容性 |
| v1.0.0 | 2026-04-07 | 初始版本，包含基本的意图识别和业务API接口 |