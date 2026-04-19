"""
意图识别核心模块 (step4_intent_core.py)

模块功能：
- 加载智能体技能库，支持多智能体隔离
- 构建大模型提示词，包含历史上下文和技能库信息
- 调用大模型进行意图识别和多意图拆解
- 处理大模型返回结果，支持EXECUTE、CLARIFY、FALLBACK三种动作
- 集成LangFuse可观测性，追踪大模型调用情况
- 支持多意图队列，处理多个技能的顺序执行

核心类：
- IntentCore: 意图识别核心类，负责整个意图识别流程

核心方法：
- process: 处理意图识别的主函数
  - 参数: context (IntentContext) - 意图上下文对象
  - 返回: IntentContext - 更新后的意图上下文，包含识别结果和动作建议

配置依赖：
- config.VOLCENGINE_API_KEY: 火山引擎API密钥
- config.VOLCENGINE_API_ENDPOINT: 火山引擎API端点
- config.VOLCENGINE_MODEL: 火山引擎模型名称
- config.LLM_TIMEOUT: LLM调用超时时间
- config.INTENT_CONFIDENCE_THRESHOLD: 意图置信度阈值
- config.APP_INTENT_MAPPING: 应用意图映射文件路径
- config.INTENT_DIR: 意图配置目录
- config.LANGFUSE_ENABLED: 是否启用LangFuse
- config.LANGFUSE_PUBLIC_KEY: LangFuse公钥
- config.LANGFUSE_SECRET_KEY: LangFuse私钥
- config.LANGFUSE_HOST: LangFuse主机地址

使用示例：
```python
from intent_engine.step4_intent_core import intent_core
from backend.schemas import IntentContext

# 创建上下文对象
context = IntentContext(
    user_id="test_user",
    app_id="Lingxi",
    session_id="test_session",
    raw_query="给我比亚迪和通用电气的访前一页纸"
)

# 执行意图识别
result = intent_core.process(context)
print(f"识别结果: {result.skill_id}")
print(f"置信度: {result.confidence}")
print(f"动作: {result.action}")
print(f"动作建议: {result.action_suggestions}")
print(f"LangFuse追踪: {result.langfuse_trace_url}")
```

输出示例：
```
识别结果: 获取企业的访前一页纸文档
置信度: 0.98
动作: EXECUTE
动作建议: [{'action': 'EXECUTE', 'skill': 'SKILL_VISIT_REPORT_V1', 'parameters': {'target_company': '比亚迪'}, 'response_text': ''}, {'action': 'EXECUTE', 'skill': 'SKILL_VISIT_REPORT_V1', 'parameters': {'target_company': '通用电气'}, 'response_text': ''}]
LangFuse追踪: https://cloud.langfuse.com/project/pk_lf_xxx/traces/xxx
```

设计特点：
- 支持智能体隔离，每个智能体有独立的技能库
- 多意图识别，支持批量处理多个技能
- 自动构建提示词，包含历史上下文和技能库信息
- 容错处理，大模型调用失败时返回兜底响应
- 集成LangFuse可观测性，提供详细的调用追踪
- 向后兼容，支持旧版本的意图识别格式
"""
import json
import os
import requests
import time
from typing import Dict, Any

from backend.schemas import IntentContext
from backend.config import config
from backend.core.exceptions import LLMError

# 初始化 LangFuse（延迟初始化，避免启动时出错）
_langfuse = None

def _get_langfuse():
    """延迟初始化 LangFuse"""
    global _langfuse
    if _langfuse is None and config.LANGFUSE_ENABLED:
        try:
            from langfuse import Langfuse
            _langfuse = Langfuse(
                public_key=config.LANGFUSE_PUBLIC_KEY,
                secret_key=config.LANGFUSE_SECRET_KEY,
                host=config.LANGFUSE_HOST
            )
        except Exception as e:
            print(f"[LangFuse] 初始化失败: {e}")
            _langfuse = False
    return _langfuse if _langfuse else None

class IntentCore:
    def __init__(self):
        self.intent_lib = self._load_intent_lib()
        self.app_intent_mapping = self._load_app_intent_mapping()
    
    def _load_intent_lib(self) -> Dict[str, Any]:
        """加载意图库"""
        intent_lib = {}
        self.agent_intent_map = {}  # 按agent_id索引的意图映射
        
        try:
            # 先加载app_intent.json，获取智能体与意图的映射
            app_intent_map = {}
            if os.path.exists(config.APP_INTENT_MAPPING):
                with open(config.APP_INTENT_MAPPING, 'r', encoding='utf-8') as f:
                    app_intent_data = json.load(f)
                    for item in app_intent_data.get('intent', []):
                        agent_id = item.get('agent_id')
                        skill_ids = item.get('skill_id', [])
                        app_intent_map[agent_id] = skill_ids
            
            # 加载智能体文件夹下的技能文件（只在智能体文件夹中查找）
            for agent_id in app_intent_map.keys():
                agent_dir = os.path.join(config.INTENT_DIR, agent_id)
                if os.path.isdir(agent_dir):
                    for filename in os.listdir(agent_dir):
                        if filename.endswith('.json'):
                            filepath = os.path.join(agent_dir, filename)
                            with open(filepath, 'r', encoding='utf-8') as f:
                                intent_data = json.load(f)
                                # 确保agent_id字段存在
                                intent_data['agent_id'] = agent_id
                                intent_id = intent_data.get('skill_id', intent_data.get('intent_id', ''))
                                
                                if intent_id:
                                    intent_lib[intent_id] = intent_data
                                    
                                    # 按agent_id索引
                                    if agent_id not in self.agent_intent_map:
                                        self.agent_intent_map[agent_id] = []
                                    # 避免重复添加
                                    if not any(item.get('skill_id') == intent_id or item.get('intent_id') == intent_id for item in self.agent_intent_map[agent_id]):
                                        self.agent_intent_map[agent_id].append(intent_data)
            
            # 根据app_intent.json更新agent_intent_map
            for agent_id, skill_ids in app_intent_map.items():
                app_intents = []
                for skill_id in skill_ids:
                    # 查找对应的意图文件（只在智能体文件夹中查找）
                    found = False
                    agent_dir = os.path.join(config.INTENT_DIR, agent_id)
                    if os.path.isdir(agent_dir):
                        for filename in os.listdir(agent_dir):
                            if filename.endswith('.json'):
                                filepath = os.path.join(agent_dir, filename)
                                with open(filepath, 'r', encoding='utf-8') as f:
                                    intent_data = json.load(f)
                                    file_skill_id = intent_data.get('skill_id', intent_data.get('intent_id', ''))
                                    if file_skill_id == skill_id:
                                        app_intents.append(intent_data)
                                        found = True
                                        break
                    if not found:
                        # 如果找不到，尝试用文件名前缀匹配（只在智能体文件夹中查找）
                        if os.path.isdir(agent_dir):
                            for filename in os.listdir(agent_dir):
                                if (filename.startswith(skill_id) and filename.endswith('.json')):
                                    filepath = os.path.join(agent_dir, filename)
                                    with open(filepath, 'r', encoding='utf-8') as f:
                                        intent_data = json.load(f)
                                        app_intents.append(intent_data)
                                        found = True
                                        break
                self.agent_intent_map[agent_id] = app_intents
                
        except Exception as e:
            raise LLMError(f"加载意图库失败: {e}")
        return intent_lib
    
    def _load_app_intent_mapping(self) -> Dict[str, Any]:
        """加载应用意图映射"""
        try:
            with open(config.APP_INTENT_MAPPING, 'r', encoding='utf-8') as f:
                data = json.load(f)
                mapping = {}
                for item in data.get('intent', []):
                    agent_id = item.get('agent_id')
                    skill_ids = item.get('skill_id', [])
                    mapping[agent_id] = skill_ids
                return mapping
        except Exception:
            return {}
    
    def _build_prompt(self, context: IntentContext) -> str:
        """构建大模型 prompt
        
        Args:
            context (IntentContext): 意图上下文对象
            
        Returns:
            str: 构建好的提示词
            
        Raises:
            LLMError: 当提示词文件不存在时抛出
        """
        import datetime
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 使用完整的历史上下文（最近3轮）
        history_context = context.history_context or "无"
        
        # 构建技能库列表（只包含当前app_id相关的技能）
        intent_list = []
        app_id = context.app_id or 'Lingxi'  # 默认使用Lingxi
        
        # 获取当前app_id的技能
        relevant_intents = []
        if app_id in self.agent_intent_map:
            relevant_intents = self.agent_intent_map[app_id]
        else:
            # 如果没有找到，使用所有技能（向后兼容）
            relevant_intents = list(self.intent_lib.values())
        
        for intent_data in relevant_intents:
            # 使用 skill_id 和 skill_description 字段
            skill_id = intent_data.get('skill_id', intent_data.get('intent_id', ''))
            skill_name = intent_data.get('skill_description', intent_data.get('skill_name', intent_data.get('intent_name', '')))
            keywords = intent_data.get('trigger_keywords', [])
            required_slots = [slot['slot_key'] for slot in intent_data.get('slots', []) if slot.get('is_required', False)]
            intent_list.append(f"- {skill_id}: {skill_name} (关键词: {', '.join(keywords)}, 必填槽位: {', '.join(required_slots)})")
        
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
        prompt = prompt.replace('{{intent_list}}', chr(10).join(intent_list))
        
        return prompt
    
    def _call_llm(self, prompt: str, context: IntentContext = None) -> Any:
        """调用大模型"""
        langfuse = _get_langfuse()
        trace = None
        generation = None
        trace_url = None
        
        if langfuse and context:
            try:
                trace = langfuse.trace(
                    name="intent_recognition",
                    metadata={
                        "session_id": context.session_id,
                        "user_id": context.user_id,
                        "app_id": context.app_id,
                        "raw_query": context.raw_query
                    }
                )
                generation = trace.generation(
                    name="llm_intent_parsing",
                    input=prompt,
                    model=config.VOLCENGINE_MODEL,
                    metadata={"prompt_template": "step4_prompt"}
                )
                trace_url = f"{config.LANGFUSE_HOST}/project/{langfuse.public_key}/traces/{trace.id}" if trace else None
                context.langfuse_trace_url = trace_url
            except Exception as e:
                print(f"[LangFuse] 创建trace失败: {e}")
        
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
                "model": config.VOLCENGINE_MODEL,
                # 支持思考程度可调节（reasoning effort）：分为 minimal、low、medium、high 四种模式，其中minimal为不思考
                "reasoning_effort": "minimal",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1
            }
            
            response = requests.post(
                config.VOLCENGINE_API_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=config.LLM_TIMEOUT
            )
            
            duration = time.time() - start_time
            
            response.raise_for_status()
            result_data = response.json()
            
            assistant_message = result_data.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            try:
                result = json.loads(assistant_message)
            except json.JSONDecodeError:
                import re
                json_pattern = r'(\{[\s\S]*?\}|\[[\s\S]*?\])'
                json_match = re.search(json_pattern, assistant_message)
                if json_match:
                    try:
                        result = json.loads(json_match.group())
                    except json.JSONDecodeError:
                        raise LLMError("无法解析大模型返回的 JSON")
                else:
                    raise LLMError("大模型返回中未找到 JSON")
            
            if generation:
                try:
                    usage_info = result_data.get('usage', {})
                    generation.end(
                        output=result, 
                        usage={
                            "cost": usage_info.get('total_tokens', 0),
                            "latency": duration
                        }
                    )
                except: pass
            
            return result
            
        except Exception as e:
            if generation:
                try:
                    generation.end(output={"error": str(e)}, status="error")
                except: pass
            raise LLMError(f"大模型调用失败: {e}")
    
    def process(self, context: IntentContext) -> IntentContext:
        """处理意图识别"""
        print(f"[STEP4] Processing intent for query: {context.raw_query}")
        # 构建 prompt
        prompt = self._build_prompt(context)
        # 保存 prompt 到 context
        context.prompt = prompt
        
        # 调用大模型
        try:
            print("[STEP4] Calling LLM...")
            result = self._call_llm(prompt, context)
            
            # 保存大模型原始返回结果（用于调试）
            print(f"[STEP4] LLM result: {result}")
            context.llm_raw_response = result
            print(f"[STEP4] Set llm_raw_response: {context.llm_raw_response}")
            
            # 保存模型名称
            context.model_name = config.VOLCENGINE_MODEL
            
            # 根据新提示词约定，result必须是数组
            if not isinstance(result, list):
                # 如果返回的不是数组，尝试将其包装为数组
                print("[STEP4] Converting single object to array")
                result = [result]
            
            # 处理数组中的意图
            print("[STEP4] Processing intent array")
            action_suggestions = []
            
            # 处理第一个意图作为主要意图
            first_intent = result[0]
            context.final_query = context.normalized_query or context.raw_query
            context.skill_id = first_intent.get('intent', 'unknown')
            context.confidence = first_intent.get('confidence', 0.0)
            
            # 更新槽位（主要用第一个意图的槽位）
            if 'slots' in first_intent and first_intent['slots']:
                context.slots_state.update(first_intent['slots'])
            
            # 处理动作（主要用第一个意图的动作）
            action = first_intent.get('action', 'FALLBACK')
            response_text = first_intent.get('response_text', '')
            
            # 存储动作和响应文本，供 dispatcher 使用
            context.action = action
            context.response_text = response_text
            
            # 构建动作建议列表 - 包含数组中所有意图
            for intent in result:
                action_suggestion = {
                    "action": intent.get('action', 'EXECUTE'),
                    "skill": intent.get('skill', ''),
                    "parameters": intent.get('parameters', {}),
                    "response_text": intent.get('response_text', '')
                }
                action_suggestions.append(action_suggestion)
            
            # 更新动作建议列表
            context.action_suggestions = action_suggestions
            
            # 设置第一个动作建议作为单独的action_suggestion（向后兼容）
            context.action_suggestion = action_suggestions[0] if action_suggestions else None
            
            # 置信度阈值判断
            if context.confidence < config.INTENT_CONFIDENCE_THRESHOLD:
                context.skill_id = 'chitchat'
                
        except Exception as e:
            # 容错处理
            print(f"[STEP4] Error: {e}")
            import traceback
            traceback.print_exc()
            context.final_query = context.normalized_query or context.raw_query
            context.skill_id = 'unknown'
            context.confidence = 0.0
            context.llm_raw_response = []
            context.action = 'FALLBACK'
            context.response_text = '系统处理异常，请稍后重试'
            context.model_name = config.VOLCENGINE_MODEL
            context.action_suggestion = None
            context.action_suggestions = []
        
        print(f"[STEP4] Returning context with llm_raw_response: {context.llm_raw_response}")
        print(f"[STEP4] Returning context with action_suggestions: {context.action_suggestions}")
        return context


# 导出实例
intent_core = IntentCore()
