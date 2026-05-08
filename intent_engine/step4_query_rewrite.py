"""
Query改写模块 (step4_query_rewrite.py)

模块功能：
- 调用大模型对用户查询进行改写
- 处理模糊表达（如"第二个"、"他的贷款"等）
- 保持原始查询的核心意图
- 支持降级处理：如果改写失败，使用原始query

核心类：
- QueryRewriter: Query改写类，负责调用大模型改写query

核心方法：
- process: 处理query改写
  - 参数: context (IntentContext) - 意图上下文对象
  - 返回: IntentContext - 更新后的意图上下文，包含改写后的query

技术细节：
- 使用doubao-seed-2-0-mini-260215模型
- temperature设为0
- 使用step4_prompt.md作为提示词
- 输出：仅包含改写后的字符串

使用示例：
```python
from intent_engine.step4_query_rewrite import query_rewriter
from backend.schemas import IntentContext

# 创建上下文对象
context = IntentContext(
    user_id="test_user",
    app_id="Lingxi",
    session_id="test_session",
    raw_query="第二个"
)

# 执行query改写
result = query_rewriter.process(context)
print(f"改写后的query: {result.rewritten_query}")
```
"""
import json
import os
import requests
import time
import datetime

from backend.schemas import IntentContext
from backend.config import config
from backend.core.exceptions import LLMError


class QueryRewriter:
    """Query改写类，负责调用大模型改写query"""
    
    def __init__(self):
        pass
    
    def _build_prompt(self, context: IntentContext) -> str:
        """构建大模型 prompt
        
        Args:
            context (IntentContext): 意图上下文对象
            
        Returns:
            str: 构建好的提示词
            
        Raises:
            LLMError: 当提示词文件不存在时抛出
        """
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 使用完整的历史上下文（最近3轮）
        history_context = context.history_context or "无"
        
        # 读取 step4_prompt.md 文件
        prompt_path = os.path.join(os.path.dirname(__file__), 'step4_prompt.md')
        if not os.path.exists(prompt_path):
            # 如果文件不存在，抛出异常
            raise LLMError(f"提示词文件不存在: {prompt_path}")
        
        # 从文件读取提示词并替换占位符
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt = f.read()
        
        # 替换占位符
        prompt = prompt.replace('{{current_time}}', current_time)
        prompt = prompt.replace('{{history_context}}', history_context)
        prompt = prompt.replace('{{normalized_query}}', context.normalized_query or context.raw_query)
        
        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """调用大模型进行query改写
        
        Args:
            prompt (str): 提示词
            
        Returns:
            str: 改写后的query
            
        Raises:
            LLMError: 当大模型调用失败时抛出
        """
        start_time = time.time()
        
        if not config.VOLCENGINE_API_KEY:
            # 如果没有API Key，抛出异常
            raise LLMError("火山引擎API密钥未配置，请在.env文件中设置VOLCENGINE_API_KEY")
        
        try:
            headers = {
                "Authorization": f"Bearer {config.VOLCENGINE_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "doubao-seed-2-0-mini-260215",
                "reasoning_effort": "minimal",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0
            }
            
            response = requests.post(
                config.VOLCENGINE_API_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=config.LLM_TIMEOUT
            )
            
            response.raise_for_status()
            result_data = response.json()
            
            assistant_message = result_data.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # 清理结果，去除多余的空白字符
            assistant_message = assistant_message.strip()
            
            return assistant_message
            
        except Exception as e:
            raise LLMError(f"大模型调用失败: {e}")
    
    def process(self, context: IntentContext) -> IntentContext:
        """处理query改写
        
        Args:
            context (IntentContext): 意图上下文对象
            
        Returns:
            IntentContext: 更新后的意图上下文，包含改写后的query
        """
        print(f"[STEP4] Processing query rewrite for: {context.raw_query}")
        
        try:
            # 构建prompt
            prompt = self._build_prompt(context)
            # 保存prompt到context
            context.step4_prompt = prompt
            
            # 保存输入信息（用于前端展示）
            import datetime
            context.step4_input_info = {
                "current_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "history_context": context.history_context or "无",
                "normalized_query": context.normalized_query or context.raw_query
            }
            
            # 调用大模型
            print("[STEP4] Calling LLM for query rewrite...")
            rewritten_query = self._call_llm(prompt)
            
            # 保存大模型原始返回结果
            print(f"[STEP4] LLM rewrite result: {rewritten_query}")
            context.step4_llm_raw_response = rewritten_query
            
            # 保存改写后的query
            if rewritten_query and len(rewritten_query) > 0:
                context.rewritten_query = rewritten_query
                context.final_query = rewritten_query
            else:
                # 如果改写失败，降级为使用原始query
                print("[STEP4] Query rewrite failed, falling back to original query")
                context.rewritten_query = context.normalized_query or context.raw_query
                context.final_query = context.normalized_query or context.raw_query
            
        except Exception as e:
            # 容错处理
            print(f"[STEP4] Error: {e}")
            import traceback
            traceback.print_exc()
            
            # 降级为使用原始query
            context.rewritten_query = context.normalized_query or context.raw_query
            context.final_query = context.normalized_query or context.raw_query
            context.step4_llm_raw_response = None
        
        print(f"[STEP4] Returning context with rewritten_query: {context.rewritten_query}")
        return context


# 导出实例
query_rewriter = QueryRewriter()
