"""
FastAPI 应用入口 (main.py)

模块功能：
- 创建并配置 FastAPI 应用实例
- 挂载静态文件，提供前端页面访问
- 注册 API 路由，包括数据查询、访前一页纸和企业信息接口
- 提供意图识别核心接口，执行完整的意图识别流水线
- 提供健康检查接口，用于监控服务状态

核心接口：
- /intent/recognize: 意图识别接口，接收用户查询并返回识别结果
- /health: 健康检查接口，返回服务状态信息

路由注册：
- data_query_router: 数据查询相关接口（存款、贷款、结算分）
- visit_report_router: 访前一页纸相关接口
- companies_router: 企业信息相关接口

静态文件：
- 挂载 /lingxi 路径，提供前端页面访问

配置依赖：
- config.APP_NAME: 应用名称
- config.VERSION: 应用版本
- config.DEBUG: 是否开启调试模式

使用示例：
```bash
# 启动服务
python main.py

# 访问前端页面
http://localhost:8000/lingxi/index_v2.html

# 调用意图识别接口
curl -X POST "http://localhost:8000/intent/recognize" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "app_id": "Lingxi",
    "session_id": "test_session",
    "raw_query": "给我比亚迪的存款信息"
  }'

# 访问健康检查接口
curl "http://localhost:8000/health"
```

设计特点：
- 使用 FastAPI 框架，提供自动 API 文档生成
- 集成意图识别流水线，实现完整的意图识别流程
- 支持静态文件服务，提供前端页面访问
- 统一的异常处理，确保服务稳定性
- 可配置的服务参数，支持不同环境部署
"""
import sys
import os

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from schemas import IntentContext
from core.pipeline import pipeline
from config import config
from api.data_query import router as data_query_router
from api.visit_report import router as visit_report_router
from api.companies import router as companies_router
from log_manager import interaction_logger
from intent_engine.step2_context import context_manager

# 创建 FastAPI 应用
app = FastAPI(
    title=config.APP_NAME,
    version=config.VERSION,
    description="银行意图识别引擎 API"
)

# 添加 CORS 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有 HTTP 头部
)

# 挂载静态文件
import os
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "lingxi")
app.mount("/lingxi", StaticFiles(directory=frontend_dir), name="lingxi")

# 注册路由
app.include_router(data_query_router)
app.include_router(visit_report_router)
app.include_router(companies_router)


@app.post("/intent/recognize")
async def recognize_intent(context: IntentContext):
    """
    意图识别接口
    
    - **user_id**: 用户ID
    - **app_id**: 应用ID (lingxi, guangnian)
    - **session_id**: 会话ID
    - **raw_query**: 用户原始查询
    """
    try:
        # 执行流水线
        result = pipeline.process(context)
        # 打印调试信息
        print(f"[API] LLM raw response: {result.llm_raw_response}")
        
        # 记录完整交互日志
        interaction_logger.log_interaction(
            user_id=context.user_id,
            app_id=context.app_id,
            session_id=context.session_id,
            context=context,
            result=result
        )
        
        # 直接返回result，让Pydantic自动处理序列化
        return result
    except Exception as e:
        print(f"[API] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/clear-conversation")
async def clear_conversation(data: dict):
    """清空对话缓存接口
    
    - **user_id**: 用户ID
    - **app_id**: 应用ID
    - **session_id**: 会话ID
    """
    try:
        user_id = data.get('user_id', '')
        app_id = data.get('app_id', '')
        session_id = data.get('session_id', '')
        
        if not all([user_id, app_id, session_id]):
            return {
                "code": 400,
                "message": "缺少必要参数：user_id, app_id, session_id"
            }
        
        success = context_manager.clear_context(app_id, user_id, session_id)
        
        if success:
            return {
                "code": 200,
                "message": "对话缓存已清空"
            }
        else:
            return {
                "code": 500,
                "message": "清空对话缓存失败"
            }
    except Exception as e:
        print(f"[API] Error clearing conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "app_name": config.APP_NAME,
        "version": config.VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=config.DEBUG
    )
