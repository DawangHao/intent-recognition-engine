"""
总控流水线模块 (pipeline.py)

模块功能：
- 协调执行完整的意图识别流程
- 集成各个步骤的处理逻辑
- 记录各步骤的执行时间
- 提供全局容错处理
- 确保意图识别流程的完整性和健壮性

核心类：
- Pipeline: 流水线类，负责协调执行各个步骤

核心方法：
- process: 执行完整的意图识别流水线
  - 参数: context (IntentContext) - 意图上下文对象
  - 返回: IntentContext - 处理后的意图上下文对象

流水线步骤：
1. 安全围栏 (Guardrail) - 检查用户输入是否包含敏感内容
2. 上下文加载 (Context loading) - 加载历史对话上下文
3. 实体提取 (Entity extraction) - 从用户输入中提取企业实体
4. 技能识别 (Skill recognition) - 调用大模型进行意图识别
5. 任务分发 (Dispatch) - 处理大模型返回结果，构建动作建议
6. 保存上下文 (Save context) - 保存本轮对话上下文到 Redis

使用示例：
```python
from backend.core.pipeline import pipeline
from schemas import IntentContext

# 创建意图上下文对象
context = IntentContext(
    user_id="test_user",
    app_id="Lingxi",
    session_id="test_session",
    raw_query="给我比亚迪的存款信息"
)

# 执行流水线
result = pipeline.process(context)
print(f"技能识别结果: {result.skill_id}")
print(f"置信度: {result.confidence}")
print(f"动作建议: {result.action_suggestions}")
print(f"响应文本: {result.response_text}")
print(f"各步骤耗时: step1={result.step1_duration:.4f}s, step2={result.step2_duration:.4f}s, step3={result.step3_duration:.4f}s, step4={result.step4_duration:.4f}s, step5={result.step5_duration:.4f}s, step6={result.step6_duration:.4f}s")
```

设计特点：
- 模块化设计，各步骤职责明确
- 完整的错误处理，确保系统稳定性
- 详细的日志记录，便于调试和监控
- 性能监控，记录各步骤执行时间
- 支持多意图队列，处理多个技能的顺序执行
- 向后兼容，支持旧版本的意图识别格式
"""
import time

from schemas import IntentContext
from intent_engine.step1_guardrail import guardrail
from intent_engine.step2_context import context_manager
from intent_engine.step3_extractor import extract_entities
from intent_engine.step4_intent_core import intent_core
from intent_engine.step5_dispatcher import dispatcher

class Pipeline:
    """流水线类，负责协调执行各个意图识别步骤"""
    def process(self, context: IntentContext) -> IntentContext:
        """执行完整的意图识别流水线
        
        Args:
            context (IntentContext): 意图上下文对象
            
        Returns:
            IntentContext: 处理后的意图上下文对象
        """
        try:
            print(f"[PIPELINE] Processing query: {context.raw_query}")
            
            # 1. 安全围栏
            print("[PIPELINE] Step 1: Guardrail")
            start_time = time.time()
            context = guardrail.check(context)
            context.step1_duration = time.time() - start_time
            
            if context.is_rejected:
                context.action_suggestion = {
                    "response_type": "FALLBACK",
                    "action": "FALLBACK",
                    "response_text": context.rejection_reason or "您的请求包含敏感内容"
                }
                return context
            
            # 2. 上下文加载
            print("[PIPELINE] Step 2: Context loading")
            start_time = time.time()
            context = context_manager.load_context(context)
            context.step2_duration = time.time() - start_time
            
            # 3. 实体提取
            print("[PIPELINE] Step 3: Entity extraction")
            start_time = time.time()
            context = extract_entities(context)
            context.step3_duration = time.time() - start_time
            print(f"[PIPELINE] Ambiguous candidates: {context.ambiguous_candidates}")
            
            # 4. 技能识别
            print("[PIPELINE] Step 4: Skill recognition")
            start_time = time.time()
            context = intent_core.process(context)
            context.step4_duration = time.time() - start_time
            print(f"[PIPELINE] Skill result: {context.skill_id}, confidence: {context.confidence}")
            
            # 5. 任务分发
            print("[PIPELINE] Step 5: Dispatch")
            start_time = time.time()
            context = dispatcher.dispatch(context)
            context.step5_duration = time.time() - start_time
            
            # 6. 保存上下文
            print("[PIPELINE] Step 6: Save context")
            start_time = time.time()
            # 如果请求中已经包含response_text，直接保存
            if hasattr(context, 'response_text') and context.response_text:
                print(f"[PIPELINE] Saving context with response_text: {context.response_text}")
            context_manager.save_context(context)
            context.step6_duration = time.time() - start_time
            
        except Exception as e:
            # 全局容错处理
            print(f"[PIPELINE] Error: {e}")
            import traceback
            traceback.print_exc()
            context.action_suggestion = {
                "response_type": "FALLBACK",
                "action": "FALLBACK",
                "response_text": "系统处理异常，请稍后重试"
            }
        
        print(f"[PIPELINE] Returning context with llm_raw_response: {context.llm_raw_response}")
        return context


# 导出实例
pipeline = Pipeline()
