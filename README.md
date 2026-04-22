# 意图识别引擎

服务于中小型银行等金融机构需要**自研意图引擎**的场景。可以为各类下游智能体（如对内的CRM智能体、对外的网银手机银行等）提供统一的、高确定性的意图识别服务。

## ✨ 特性

-  **智能意图识别** - 基于大模型的多意图识别与分类
-  **中台化设计** - 一个意图引擎，同时服务多个下游智能体，意图相互隔离不打架不干扰
-  **意图库管理** - 通过JSON格式管理意图清单，稳定且高效
-  **技能注册模式** - 提供意图注册平台，智能体登记自身技能，可快速生成意图json
-  **多轮对话支持** - 支持记忆，完整的上下文管理机制
-  **实体提取器** - 支持通过数据库提取客户名称、指标名称等，简化大模型操作
-  **低参大模型，快** - 采用低参数大模型（约7B），seed-mini 不思考模式，支持2秒内识别出意图
-  **配置化设计** - 技能配置外部化，便于扩展

## 🏗️ 技术栈

| 组件 | 技术选型 |
|------|---------|
| 后端框架 | FastAPI |
| Python 版本 | 3.13 |
| 数据校验 | Pydantic v2 |
| 上下文存储 | Redis / Mock Redis |
| 实体匹配 | FlashText |
| 大模型 | 火山引擎 Doubao |
| 可观测性 | LangFuse |
| 前端 | HTML5 + CSS3 + JavaScript |

## 📁 项目结构

```
intent-recognition-engine/
├── backend/                 # 后端服务
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 全局配置
│   ├── schemas.py           # 数据模型定义
│   ├── core/                # 核心逻辑
│   │   ├── pipeline.py      # 意图识别流水线
│   │   └── exceptions.py    # 自定义异常
│   └── api/                 # API 接口
│       ├── data_query.py    # 数据查询接口
│       ├── visit_report.py  # 访谈报告接口
│       └── companies.py     # 企业信息接口
├── intent_engine/           # 意图识别引擎
│   ├── step1_guardrail.py   # 安全围栏
│   ├── step2_context.py     # 上下文管理
│   ├── step3_extractor.py   # 实体提取
│   ├── step4_intent_core.py # 意图识别核心
│   ├── step5_dispatcher.py  # 任务分发
│   └── Lingxi/              # 灵犀技能配置
├── frontend/                # 前端页面
│   └── lingxi/              # 灵犀前端
├── tests/                   # 测试用例
│   ├── unit/                # 单元测试
│   ├── integration/         # 集成测试
│   └── e2e/                 # 端到端测试
├── .env.example             # 环境变量模板
└── requirements.txt         # 项目依赖
```

## 🚀 快速开始

### 前置要求

- Python 3.13+
- Redis (可选，不使用时可使用 Mock Redis)

### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/DawangHao/intent-recognition-engine.git
cd intent-recognition-engine
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API Keys
```

5. **启动服务**
```bash
python -m backend.main
```

服务将在 `http://localhost:8000` 启动。

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定类型测试
pytest tests/unit/           # 单元测试
pytest tests/integration/    # 集成测试
pytest tests/e2e/            # 端到端测试

# 生成测试报告
pytest --cov=backend --cov=intent_engine --html=report.html
```

## 🔧 配置说明

### 环境变量

在 `.env` 文件中配置以下关键参数：

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `VOLCENGINE_API_KEY` | 火山引擎 API Key | 必填 |
| `VOLCENGINE_MODEL` | 模型名称 | doubao-seed-2-0-mini-260215 |
| `USE_REAL_REDIS` | 是否使用真实 Redis | false |
| `REDIS_HOST` | Redis 地址 | localhost |
| `REDIS_PORT` | Redis 端口 | 6379 |
| `LANGFUSE_ENABLED` | 是否启用 LangFuse | false |
| `INTENT_CONFIDENCE_THRESHOLD` | 意图置信度阈值 | 0.7 |

详细配置说明请参考 `.env.example` 文件。

## 📚 核心功能

### 意图识别流程

```
用户输入
    ↓
┌─────────────────┐
│ 1. 安全围栏     │ → 黑名单过滤 / 内容检查
└─────────────────┘
    ↓
┌─────────────────┐
│ 2. 上下文管理   │ → 加载历史对话 / 维护会话状态
└─────────────────┘
    ↓
┌─────────────────┐
│ 3. 实体提取     │ → 提取关键信息 (公司名、金额等)
└─────────────────┘
    ↓
┌─────────────────┐
│ 4. 意图识别     │ → LLM 识别用户意图
└─────────────────┘
    ↓
┌─────────────────┐
│ 5. 任务分发     │ → 调用对应技能处理
└─────────────────┘
    ↓
返回响应
```

### 支持的技能

- 📄 **访前一页纸** - 生成客户访谈报告
- 🏢 **企业推荐** - 基于客户信息推荐企业
- 💰 **存款查询** - 查询客户存款信息
- 🏦 **贷款查询** - 查询客户贷款信息
- 🧾 **结算查询** - 查询结算账户信息
- 👤 **客户卡片** - 获取客户详细信息

## 📖 API 文档

启动服务后访问：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

详细 API 文档请参考 [API接口文档.md](./API接口文档.md)

## 🧩 扩展开发

### 添加新技能

1. 在 `intent_engine/Lingxi/` 创建新的技能配置文件
2. 在 `step5_dispatcher.py` 中添加分发逻辑
3. 编写对应的 API 处理函数
4. 添加测试用例

详细开发指南请参考 [新技能开发指南.md](./新技能开发指南.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目采用 MIT 许可证。

## 📞 联系方式

- 作者: DawangHao
- 邮箱: h945587579@163.com
- GitHub: [@DawangHao](https://github.com/DawangHao)

---

⭐ 如果这个项目对你有帮助，请给个 Star！
