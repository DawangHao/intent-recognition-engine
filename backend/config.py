"""
全局配置模块 (config.py)

模块功能：
- 集中管理应用的所有配置项
- 支持从环境变量和 .env 文件加载配置
- 提供默认值，确保配置缺失时系统仍能运行
- 定义路径常量，确保文件路径的一致性

配置分类：
1. 基础配置 - 应用名称、版本、调试模式等
2. Redis 配置 - Redis 连接参数和上下文缓存设置
3. 大模型配置 - 火山引擎 API 相关配置
4. 路径配置 - 项目各目录和文件的路径
5. LangFuse 配置 - 可观测性相关配置

环境变量优先级：
- 已设置的环境变量 > .env 文件 > 默认值

使用示例：
```python
from backend.config import config

# 访问配置
print(f"应用名称: {config.APP_NAME}")
print(f"大模型: {config.VOLCENGINE_MODEL}")
print(f"数据目录: {config.DATA_DIR}")

# 检查配置
if not config.VOLCENGINE_API_KEY:
    print("警告: 未设置火山引擎 API Key")

if config.LANGFUSE_ENABLED:
    print("LangFuse 可观测性已启用")
```

配置说明：

基础配置：
- APP_NAME: 应用名称，用于API文档和健康检查
- VERSION: 应用版本号
- DEBUG: 是否开启调试模式

Redis 配置：
- USE_REAL_REDIS: 是否使用真实 Redis 服务
- REDIS_HOST: Redis 主机地址
- REDIS_PORT: Redis 端口
- REDIS_DB: Redis 数据库编号
- REDIS_PASSWORD: Redis 密码
- CONTEXT_TTL: 上下文缓存过期时间（秒）

大模型配置：
- VOLCENGINE_API_KEY: 火山引擎 API 密钥
- VOLCENGINE_API_ENDPOINT: 火山引擎 API 端点
- VOLCENGINE_MODEL: 火山引擎模型名称
- LLM_TIMEOUT: LLM 调用超时时间（秒）
- INTENT_CONFIDENCE_THRESHOLD: 意图置信度阈值

路径配置：
- BASE_DIR: backend 目录的绝对路径
- ROOT_DIR: 项目根目录的绝对路径
- DATA_DIR: 数据目录路径
- BLACKLIST_PATH: 黑名单文件路径
- CUSTOMERS_PATH: 客户数据文件路径
- INTENT_DIR: 意图配置目录
- APP_INTENT_MAPPING: 应用意图映射文件路径

LangFuse 配置：
- LANGFUSE_PUBLIC_KEY: LangFuse 公钥
- LANGFUSE_SECRET_KEY: LangFuse 私钥
- LANGFUSE_HOST: LangFuse 主机地址
- LANGFUSE_ENABLED: 是否启用 LangFuse
"""
import os
from typing import Optional
from dotenv import load_dotenv

# 加载 .env 文件（如果存在）
# 优先级：已设置的环境变量 > .env 文件
load_dotenv()

# 全局配置类
class Config:
    # ----------------------------------------
    # 基础配置
    # ----------------------------------------
    APP_NAME = "意图识别引擎"
    VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"

    # ----------------------------------------
    # Redis 配置
    # ----------------------------------------
    # 使用真实 Redis 还是本地模拟
    # - True: 使用真实 Redis 服务
    # - False: 使用 fakeredis（本地测试，无需启动 Redis 服务）
    USE_REAL_REDIS = os.getenv("USE_REAL_REDIS", "false").lower() == "true"

    # Redis 连接配置（当 USE_REAL_REDIS=True 时生效）
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")

    # 上下文缓存过期时间（秒）
    CONTEXT_TTL = int(os.getenv("CONTEXT_TTL", "3600"))

    # ----------------------------------------
    # 大模型配置
    # ----------------------------------------
    # 火山引擎 API 配置 - 从环境变量读取
    VOLCENGINE_API_KEY = os.getenv("VOLCENGINE_API_KEY", "")
    VOLCENGINE_API_ENDPOINT = os.getenv("VOLCENGINE_API_ENDPOINT", "https://ark.cn-beijing.volces.com/api/v3/chat/completions")
    VOLCENGINE_MODEL = os.getenv("VOLCENGINE_MODEL", "doubao-seed-2-0-mini-260215")
    
    # LLM 调用超时时间（秒）
    LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "30"))

    # 意图置信度阈值（低于此值视为闲聊）
    INTENT_CONFIDENCE_THRESHOLD = float(os.getenv("INTENT_CONFIDENCE_THRESHOLD", "0.7"))

    # ----------------------------------------
    # 路径配置
    # ----------------------------------------
    # 使用绝对路径，确保从任何目录运行都能正确找到文件
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # 项目根目录
    ROOT_DIR = os.path.dirname(BASE_DIR)
    DATA_DIR = os.path.join(ROOT_DIR, "data")
    BLACKLIST_PATH = os.path.join(DATA_DIR, "blacklist.txt")
    CUSTOMERS_PATH = os.path.join(DATA_DIR, "bank_customers.csv")

    # 意图配置目录
    INTENT_DIR = os.path.join(ROOT_DIR, "intent_engine")
    APP_INTENT_MAPPING = os.path.join(INTENT_DIR, "app_intent.json")

    # ----------------------------------------
    # LangFuse 可观测性配置
    # ----------------------------------------
    LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "")
    LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    LANGFUSE_ENABLED = bool(os.getenv("LANGFUSE_ENABLED", "false").lower() == "true")


# 导出配置实例
config = Config()
