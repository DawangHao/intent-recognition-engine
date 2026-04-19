# 技术实现方案（TDD）v1.0

## 1. 项目概述与设计原则

本项目旨在为银行的各类智能体（如灵犀、光年、网银客服等）提供统一的、高确定性的意图识别服务。

### 核心设计原则（Trae 编码须知）：

- **极简主义与确定性优先**： 严格遵循架构图的“简化点”，能用正则、字典、缓存解决的环节（如安全黑名单、实体精确匹配），不需要调用 LLM。
- **实战**：尽量避免硬代码编程，所有配置项都从外部文件（如 JSON、CSV）读取。
- **防御性编程**： 银行场景要求极高的容错率。每个环节必须有异常捕获，并在报错时有默认的“兜底（Fallback）”策略。

## 2. 技术栈选型

- **核心框架**： Python 3.13 + FastAPI（提供高性能 RESTful API）
- **数据校验与序列化**： Pydantic v2（用于定义严格的数据契约）
- **上下文存储**： Redis（支持真实Redis和Mock Redis）
- **快速实体匹配**： 字符串匹配算法
- **大模型接口**： 火山引擎大模型接口
- **前端技术**： HTML5 + CSS3 + JavaScript
- **前端服务器**： Python HTTP Server

## 3. 工程目录结构

```
2026.03意图识别引擎/
├── backend/                 # 后端平台
│   ├── main.py              # FastAPI 入口，组装 Pipeline
│   ├── config.py            # 全局配置 (阈值、Redis连接、大模型接口等)
│   ├── schemas.py           # 核心数据契约 (IntentContext 定义)
│   ├── core/
│   │   ├── pipeline.py      # 总控流水线逻辑
│   │   └── exceptions.py    # 自定义异常类
│   └── api/
│       ├── data_query.py     # 数据查询相关接口
│       ├── visit_report.py   # 访前一页纸相关接口
│       └── companies.py      # 企业相关接口
├── frontend/                # 前端页面
│   ├── lingxi/              # 灵犀前端
│   │   └── index_v2.html    # 灵犀前端演示页面
│   └── teaching/            # 教学步骤前端页面
├── intent_engine/           # 意图识别引擎
│   ├── step1_guardrail.py   # 安全围栏
│   ├── step2_context.py     # 上下文管理
│   ├── step3_extractor.py   # 实体提取器
│   ├── step4_intent_core.py # 意图识别核心
│   ├── step4_prompt.md      # 大模型提示词模板
│   ├── step5_dispatcher.py  # 任务分发
│   └── intent/
│       ├── CXCK.json        # 查询存款技能配置
│       ├── CXDK.json        # 查询贷款技能配置
│       ├── FQYYZ.json       # 获取访前一页纸技能配置
│       └── app_intent.json  # 应用与技能映射
├── data/
│   ├── blacklist.txt        # 合规黑名单关键词
│   ├── bank_customers.csv   # 行内客户词典
│   ├── 企业信息.csv          # 企业信息数据
│   └── 访前一页纸/           # 企业访前一页纸文档
├── requirements.txt         # 依赖清单
└── 技术实现方案（TDD）v1.0.md # 技术实现方案文档
```

## 4. 核心数据契约 (Data Contract)

所有的模块必须以 `IntentContext` 作为输入，并修改该对象的属性作为输出。`IntentContext` 包含以下核心字段：

| 字段名称 | 类型 | 描述 |
|---------|------|------|
| user_id | str | 用户ID |
| app_id | str | 来源应用，如 "Lingxi", "Guangnian" |
| session_id | str | 会话ID |
| raw_query | str | 用户原始查询 |
| normalized_query | Optional[str] | 实体改写后的查询 |
| final_query | Optional[str] | 指代消解后的最终查询 |
| skill_id | str | 识别出的技能ID |
| confidence | float | 置信度分数 |
| slots_state | Dict[str, Any] | 槽位状态 |
| is_rejected | bool | 是否被安全围栏拒绝 |
| rejection_reason | Optional[str] | 拒绝原因 |
| ambiguous_candidates | Dict[str, Any] | 歧义候选列表 |
| missing_slots | List[str] | 缺失槽位列表 |
| action | Optional[str] | 动作类型 |
| response_text | Optional[str] | 响应文本 |
| llm_raw_response | Optional[Dict[str, Any]] | 大模型原始返回结果 |
| prompt | Optional[str] | 发送给大模型的提示词 |
| model_name | Optional[str] | 使用的模型名称 |
| action_suggestion | Optional[Dict[str, Any]] | 动作建议 |
| step1_duration | Optional[float] | 安全围栏耗时 |
| step2_duration | Optional[float] | 上下文加载耗时 |
| step3_duration | Optional[float] | 实体提取耗时 |
| step4_duration | Optional[float] | 技能识别耗时 |
| step5_duration | Optional[float] | 任务分发耗时 |
| step6_duration | Optional[float] | 保存上下文耗时 |

## 5. 组件逻辑实现

### 阶段一：前置准备 (Deterministic & Contextual Layer)

#### step1_guardrail.py (安全围栏)
- **输入**：raw_query
- **逻辑**：
  - 与blacklist.txt匹配，拦截黑名单、不合规问题。
- **输出**：若命中黑名单，设置 is_rejected=True。

#### step2_context.py (上下文管理)
- **输入**：user_id、session_id、app_id
- **逻辑**：
  - 从Redis或内存缓存中加载该用户在该会话下的上一轮记录。
  - 核心更新：将上一轮的 final_query 填入本轮的 last_turn_query；将上一轮的技能和实体填入 last_turn_ 系列字段。
  - 意义：为后续的“指代消解”提供记忆。

#### step3_extractor.py (实体提取器)
- **输入**：raw_query, 企业信息数据
- **逻辑**：
  1. 从企业信息.csv或bank_customers.csv加载企业数据。
  2. 在raw_query中匹配企业名称。
  3. 处理不同场景：
     - **场景A**：完全匹配且唯一：将raw_query中的关键词替换为企业全称。
     - **场景B**：匹配但存在歧义：将关键词改写为<AMBIGUOUS_ENTITY key="关键词">，并将候选清单存入ambiguous_candidates。
     - **场景C**：未命中：保持normalized_query = raw_query。
- **输出**：更新normalized_query和ambiguous_candidates字段。

### 阶段二：核心决策 (LLM Reasoning Layer)

#### step4_intent_core.py (意图识别核心)
- **输入**：完整的IntentContext对象。
- **逻辑**：
  1. 读取step4_prompt.md中的提示词模板。
  2. 将normalized_query和上下文信息植入提示词。
  3. 调用大模型获取意图识别结果。
  4. 解析大模型返回的JSON格式结果。
  5. 更新skill_id、confidence、action等字段。
- **输出**：更新IntentContext对象的相关字段。

### 阶段三：指令下发 (Dispatch Layer)

#### step5_dispatcher.py (任务分发)
- **输入**：IntentContext对象。
- **逻辑**：
  1. 从大模型返回的结果中提取action类型。
  2. 根据action类型构建不同的action_suggestion：
     - **EXECUTE**：构建包含skill和parameters的执行指令。
     - **CLARIFY**：构建包含response_text的追问指令。
     - **FALLBACK**：构建兜底指令。
- **输出**：更新action_suggestion字段。

### 阶段四：上下文保存

- **逻辑**：将当前轮次的结果保存到Redis或内存缓存中，供下一轮使用。

## 6. 前端实现

### lingxi_ui/index_v2.html (灵犀前端演示页面)
- **功能**：
  1. 提供对话界面，接收用户输入并显示响应。
  2. 显示意图引擎处理步骤和结果。
  3. 提供快捷对话气泡，方便调试。
  4. 提供接口调试功能，可直接调用技能API。
  5. 显示每个处理步骤的耗时信息。
- **技术实现**：
  - 使用HTML5 + CSS3 + JavaScript构建。
  - 通过fetch API调用后端接口。
  - 动态更新页面内容，显示处理步骤和结果。
  - 实现企业名称自动联想功能。

## 7. API接口设计

### 意图识别接口
- **路径**：`/intent/recognize`
- **方法**：POST
- **请求体**：IntentContext对象
- **响应**：包含处理结果的JSON对象

### 企业列表接口
- **路径**：`/api/companies`
- **方法**：GET
- **参数**：keyword（企业名称关键词）
- **响应**：企业列表

### 存款查询接口
- **路径**：`/api/deposit/query`
- **方法**：POST
- **请求体**：{"company_name": "企业名称"}
- **响应**：企业存款信息

### 贷款查询接口
- **路径**：`/api/loan/query`
- **方法**：POST
- **请求体**：{"company_name": "企业名称"}
- **响应**：企业贷款信息

### 访前一页纸下载接口
- **路径**：`/api/visit-report/download`
- **方法**：POST
- **请求体**：{"company_name": "企业名称"}
- **响应**：Word文档文件

## 8. 技能清单

| 技能名称 | 技能ID | API路径 | 功能描述 |
|---------|--------|---------|----------|
| 查询存款 | SKILL_DEPOSIT_QUERY_V1 | /api/deposit/query | 查询企业存款信息 |
| 查询贷款 | SKILL_LOAN_QUERY_V1 | /api/loan/query | 查询企业贷款信息 |
| 获取访前一页纸 | SKILL_VISIT_REPORT_V1 | /api/visit-report/download | 下载企业访前一页纸文档 |

## 9. 性能优化

1. **缓存策略**：使用Redis或内存缓存存储上下文信息，减少重复计算。
2. **异步处理**：使用FastAPI的异步特性，提高并发处理能力。
3. **数据加载**：在服务启动时预加载企业信息数据，减少运行时IO操作。
4. **计时监控**：实现了每个步骤的耗时监控，便于识别性能瓶颈。

## 10. 容错机制

1. **异常捕获**：每个模块都有异常捕获机制，确保系统不会因单个环节的错误而崩溃。
2. **兜底策略**：当意图识别失败或出现其他错误时，返回FALLBACK指令。
3. **数据验证**：使用Pydantic进行数据验证，确保输入和输出的数据格式正确。
4. **空值处理**：对可能为空的字段进行合理的默认值处理。

## 11. 部署与运行

### 后端服务
```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 前端服务
```bash
# 进入前端目录
cd lingxi_ui

# 启动前端服务器
python -m http.server 8080
```

### 访问地址
- 前端页面：http://localhost:8080/index_v2.html
- API文档：http://localhost:8000/docs

## 12. 后续优化方向

1. **模型优化**：探索使用更小参数的模型，提高响应速度。
2. **实体识别增强**：引入更高级的实体识别技术，提高实体提取的准确性。
3. **上下文管理**：优化上下文存储和检索策略，提高多轮对话的连贯性。
4. **技能扩展**：支持更多类型的技能，如转账、查询余额等。
5. **前端优化**：进一步优化前端界面，提供更丰富的交互体验。

## 13. 总结

本项目实现了一个完整的银行意图识别引擎，具有以下特点：

1. **模块化设计**：将意图识别流程分解为多个独立模块，便于维护和扩展。
2. **确定性优先**：在可能的情况下使用确定性方法（如正则、字典匹配），提高系统的稳定性和响应速度。
3. **LLM集成**：在需要复杂推理的环节使用大模型，提高意图识别的准确性。
4. **上下文管理**：实现了基于Redis的上下文管理，支持多轮对话。
5. **前端演示**：提供了直观的前端演示页面，便于调试和展示。
6. **性能监控**：实现了每个步骤的耗时监控，便于识别性能瓶颈。
7. **容错机制**：完善的异常捕获和兜底策略，确保系统的稳定性。

该系统可以为银行的各类智能体提供统一的意图识别服务，支持多种业务场景，如查询存款、查询贷款、获取访前一页纸等。