"""
上下文管理模块 (step2_context.py)

模块功能：
- 管理用户对话的历史上下文信息
- 支持Redis和内存双缓存机制，确保服务重启后上下文不丢失
- 提供最近三轮对话的历史记录，用于意图识别
- 自动构建响应文本，丰富历史上下文内容

核心类：
- ContextManager: 上下文管理主类，负责加载和保存对话上下文

核心方法：
- load_context: 加载上一轮对话上下文
  - 参数: context (IntentContext) - 意图上下文对象
  - 返回: IntentContext - 更新后的意图上下文，包含历史对话信息

- save_context: 保存本轮对话上下文
  - 参数: context (IntentContext) - 意图上下文对象
  - 返回: None

配置依赖：
- config.USE_REAL_REDIS: 是否使用真实Redis
- config.REDIS_HOST: Redis主机地址
- config.REDIS_PORT: Redis端口
- config.REDIS_DB: Redis数据库
- config.REDIS_PASSWORD: Redis密码
- config.CONTEXT_TTL: 上下文缓存过期时间（秒）

使用示例：
```python
from intent_engine.step2_context import context_manager
from backend.schemas import IntentContext

# 创建上下文对象
context = IntentContext(
    user_id="test_user",
    app_id="Lingxi",
    session_id="test_session",
    raw_query="查比亚迪的存款"
)

# 加载历史上下文
loaded_context = context_manager.load_context(context)
print(f"历史上下文: {loaded_context.history_context}")

# 处理业务逻辑...
context.response_text = "已查询比亚迪的存款信息"

# 保存本轮上下文
context_manager.save_context(context)
```

设计特点：
- 支持真实Redis和fakeredis两种模式
- 内存缓存备份，确保服务重启后上下文不丢失
- 自动构建响应文本，增强历史记录的可读性
- 只保留最近3轮对话，避免历史记录过长
- 容错处理，Redis操作失败不影响主流程
"""
import json
import time

from backend.schemas import IntentContext
from backend.config import config
from backend.core.exceptions import RedisError

# 根据配置选择 Redis 实现
if config.USE_REAL_REDIS:
    import redis
else:
    import fakeredis

class ContextManager:
    """上下文管理类，负责加载和保存对话上下文"""
    def __init__(self):
        """初始化上下文管理器
        
        - 初始化Redis客户端
        - 初始化内存缓存
        """
        self.redis_client = self._init_redis()
        # 内存缓存，用于fake Redis，确保服务重启后上下文不丢失
        self.memory_cache = {}
    
    def _init_redis(self):
        """初始化 Redis 客户端
        
        Returns:
            redis.Redis or fakeredis.FakeRedis: Redis客户端实例
            
        Raises:
            RedisError: Redis初始化失败时抛出
        """
        try:
            if config.USE_REAL_REDIS:
                return redis.Redis(
                    host=config.REDIS_HOST,
                    port=config.REDIS_PORT,
                    db=config.REDIS_DB,
                    password=config.REDIS_PASSWORD
                )
            else:
                return fakeredis.FakeRedis()
        except Exception as e:
            raise RedisError(f"Redis 初始化失败: {e}")
    
    def _get_context_key(self, app_id: str, user_id: str, session_id: str) -> str:
        """生成上下文缓存键
        
        Args:
            app_id (str): 应用ID
            user_id (str): 用户ID
            session_id (str): 会话ID
            
        Returns:
            str: 上下文缓存键
        """
        # 使用小写的app_id，确保大小写不敏感
        return f"intent_context:{app_id.lower()}:{user_id}:{session_id}"
    
    def load_context(self, context: IntentContext) -> IntentContext:
        """加载上一轮上下文
        
        Args:
            context (IntentContext): 意图上下文对象
            
        Returns:
            IntentContext: 更新后的意图上下文，包含历史对话信息
        """
        try:
            key = self._get_context_key(context.app_id, context.user_id, context.session_id)
            print(f"[CONTEXT] Loading context with key: {key}")
            
            # 首先尝试从Redis加载
            cached_data = self.redis_client.get(key)
            
            # 如果Redis中没有，尝试从内存缓存加载（用于fake Redis服务重启的情况）
            if not cached_data and key in self.memory_cache:
                print(f"[CONTEXT] Loading from memory cache")
                cached_data = self.memory_cache[key]
            
            if cached_data:
                print(f"[CONTEXT] Found cached context: {cached_data}")
                context_history = json.loads(cached_data)
                
                # 构建历史上下文字符串，包含最近三轮对话
                history_str = ""
                # 取最近的三轮对话
                start_idx = max(0, len(context_history) - 3)
                for i in range(start_idx, len(context_history)):
                    turn = context_history[i]
                    # 将时间戳转换为时:分:秒格式
                    timestamp_str = time.strftime("%H:%M:%S", time.localtime(turn['timestamp']))
                    history_str += f"第{i+1}轮对话（时间：{timestamp_str}）\n"
                    history_str += f"（1）用户输入：{turn['raw_query']}\n"
                    history_str += f"（2）返回用户：{turn['response_text']}\n\n"
                
                # 保存历史上下文到context
                context.history_context = history_str.strip() if history_str else "无"
                
                # 保存上一轮的具体信息
                if context_history:
                    last_turn = context_history[-1]
                    context.last_turn_query = last_turn.get('raw_query')
                    context.last_turn_skill = last_turn.get('skill_id')
                    context.last_turn_entities = last_turn.get('slots_state', {})
                    context.last_turn_response = last_turn.get('response_text')
                    print(f"[CONTEXT] Loaded context: last_turn_query={context.last_turn_query}, last_turn_response={context.last_turn_response}")
            else:
                print(f"[CONTEXT] No cached context found for key: {key}")
                # 打印当前上下文信息，以便调试
                print(f"[CONTEXT] Current context: app_id={context.app_id}, user_id={context.user_id}, session_id={context.session_id}")
                context.history_context = "无"
        except Exception as e:
            print(f"[CONTEXT] Error loading context: {e}")
            # 容错处理，加载失败不影响主流程
            context.history_context = "无"
            pass
        
        return context
    
    def save_context(self, context: IntentContext):
        """保存本轮上下文
        
        Args:
            context (IntentContext): 意图上下文对象
        """
        try:
            key = self._get_context_key(context.app_id, context.user_id, context.session_id)
            print(f"[CONTEXT] Saving context with key: {key}")
            
            # 构建响应文本
            response_text = context.response_text
            if not response_text and hasattr(context, 'action_suggestion') and context.action_suggestion:
                action = context.action_suggestion.get('action')
                if action == 'EXECUTE':
                    skill = context.action_suggestion.get('skill', '')
                    parameters = context.action_suggestion.get('parameters', {})
                    # 根据技能ID生成中文名称
                    skill_name_map = {
                        'SKILL_DEPOSIT_QUERY_V1': '查询企业的本外币合计对公存款余额',
                        'SKILL_LOAN_QUERY_V1': '查询企业的本外币合计总贷款余额',
                        'SKILL_VISIT_REPORT_V1': '获取企业的访前一页纸',
                        'SKILL_SETTLEMENT_QUERY_V1': '查询企业结算分'
                    }
                    skill_name = skill_name_map.get(skill, skill)
                    # 提取参数中的企业名称
                    target_company = parameters.get('target_company', '')
                    # 生成更自然的响应文本
                    if skill == 'SKILL_DEPOSIT_QUERY_V1':
                        response_text = f"查询{target_company}的存款余额"
                    elif skill == 'SKILL_LOAN_QUERY_V1':
                        response_text = f"查询{target_company}的贷款余额"
                    elif skill == 'SKILL_VISIT_REPORT_V1':
                        response_text = f"获取{target_company}的访前一页纸"
                    elif skill == 'SKILL_SETTLEMENT_QUERY_V1':
                        response_text = f"查询{target_company}的结算分"
                    else:
                        response_text = f"执行{skill_name}"
                elif action == 'CLARIFY':
                    # 直接使用澄清文本
                    response_text = context.action_suggestion.get('response_text', '')
                elif action == 'FALLBACK':
                    # 直接使用兜底文本
                    response_text = context.action_suggestion.get('response_text', '')
            
            # 构建本轮上下文数据
            current_turn = {
                'timestamp': time.time(),
                'raw_query': context.raw_query,  # 用户输入
                'final_query': context.final_query,
                'skill_id': context.skill_id,
                'action': context.action,
                'response_text': response_text,  # 构建的响应文本
                'slots_state': context.slots_state
            }
            
            # 加载现有历史记录
            cached_data = self.redis_client.get(key)
            if not cached_data and key in self.memory_cache:
                cached_data = self.memory_cache[key]
            
            context_history = []
            if cached_data:
                context_history = json.loads(cached_data)
            
            # 添加本轮对话到历史记录
            context_history.append(current_turn)
            
            # 只保留最近3轮对话
            if len(context_history) > 3:
                context_history = context_history[-3:]
            
            context_json = json.dumps(context_history)
            print(f"[CONTEXT] Context data to save: {context_history}")
            
            # 保存到Redis
            self.redis_client.setex(
                key,
                config.CONTEXT_TTL,
                context_json
            )
            
            # 同时保存到内存缓存，用于fake Redis服务重启的情况
            self.memory_cache[key] = context_json
            
            print(f"[CONTEXT] Context saved successfully")
        except Exception as e:
            print(f"[CONTEXT] Error saving context: {e}")
            # 容错处理，保存失败不影响主流程
            pass


# 导出实例
context_manager = ContextManager()
