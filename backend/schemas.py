"""
核心数据契约模块 (schemas.py)

模块功能：
- 定义意图识别系统的核心数据结构
- 提供数据验证和类型提示
- 规范系统内部数据流转格式
- 支持自动序列化和反序列化

核心类：
- IntentContext: 意图上下文对象，贯穿整个意图识别流程

IntentContext 字段说明：

1. 基础路由信息 (Routing & Tracking)
   - user_id: 用户ID，用于标识用户身份
   - app_id: 来源应用ID，如 "lingxi", "guangnian"
   - session_id: 会话ID，用于追踪对话上下文

2. 上下文记忆 (Context Memory)
   - last_turn_query: 上一轮用户输入
   - last_turn_skill: 上一轮使用的技能ID
   - last_turn_entities: 上一轮的实体状态
   - last_turn_response: 上一轮的响应文本
   - history_context: 近三轮上下文信息（用于前端展示）

3. 本轮 Query 演进链 (Query Evolution)
   - raw_query: 用户原始查询
   - normalized_query: 实体提取后的标准化查询
   - final_query: 最终处理后的查询

4. 技能与槽位状态 (Skill & Slots State)
   - skill_id: 识别出的技能ID
   - confidence: 意图识别置信度
   - slots_state: 槽位键值对
   - is_rejected: 是否被安全围栏拒绝
   - rejection_reason: 拒绝原因
   - ambiguous_candidates: 歧义候选列表
   - missing_slots: 缺失槽位列表

5. 动作和响应
   - action: 动作类型 (EXECUTE, CLARIFY, FALLBACK)
   - response_text: 响应文本

6. 调试信息
   - llm_raw_response: 大模型原始返回结果
   - prompt: 发送给大模型的提示词
   - model_name: 使用的模型名称
   - langfuse_trace_url: LangFuse 追踪 URL

7. 性能指标
   - step1_duration: 安全围栏耗时
   - step2_duration: 上下文加载耗时
   - step3_duration: 实体提取耗时
   - step4_duration: 技能识别耗时
   - step5_duration: 任务分发耗时
   - step6_duration: 保存上下文耗时

8. 动作建议
   - action_suggestion: 单个动作建议（向后兼容）
   - action_suggestions: 动作建议列表，支持多意图队列

使用示例：
```python
from backend.schemas import IntentContext

# 创建意图上下文对象
context = IntentContext(
    user_id="test_user",
    app_id="Lingxi",
    session_id="test_session",
    raw_query="给我比亚迪的存款信息"
)

# 访问和修改字段
context.skill_id = "SKILL_DEPOSIT_QUERY_V1"
context.confidence = 0.95
context.slots_state = {"target_company": "比亚迪"}
context.action = "EXECUTE"
context.response_text = "查询比亚迪的存款"

# 序列化
context_dict = context.model_dump()
print(f"Context: {context_dict}")

# 反序列化
new_context = IntentContext(**context_dict)
print(f"New context: {new_context.skill_id}")
```

设计特点：
- 使用 Pydantic V2 语法，提供类型提示和数据验证
- 字段默认值合理，确保系统健壮性
- 支持任意类型字段，适应复杂数据结构
- 字段注释清晰，便于理解和维护
- 贯穿整个意图识别流程，作为数据传递的核心载体
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

class IntentContext(BaseModel):
    # ---------------------------------------------------------
    # 1. 基础路由信息 (Routing & Tracking)
    # ---------------------------------------------------------
    user_id: str
    app_id: str                              # 来源应用，例如: "lingxi", "guangnian", "oa_agent"
    session_id: str

    # ---------------------------------------------------------
    # 上下文记忆 (Context Memory - 由M2从Redis加载)
    # ---------------------------------------------------------
    last_turn_query: Optional[str] = None    # 上一轮用户输入
    last_turn_skill: Optional[str] = None   # 上一轮的技能ID
    last_turn_entities: Dict[str, Any] = Field(default_factory=dict) # 上一轮的实体状态
    last_turn_response: Optional[str] = None  # 上一轮灵犀的反馈信息
    history_context: Optional[str] = None     # 近两轮上下文信息（用于前端展示）

    # ---------------------------------------------------------
    # 3. 本轮 Query 演进链 (Query Evolution)
    # ---------------------------------------------------------
    raw_query: str                           # 1. 用户原话: "帮我查一下他那个账户还有多少钱"
    normalized_query: Optional[str] = None   # 2. 实体改写(泛化): "帮我查一下[PRONOUN][ACCOUNT_TYPE]还有多少钱"
    final_query: Optional[str] = None        # 3. 指代消解后: "帮我查一下张三的招商银行卡还有多少钱"

    # ---------------------------------------------------------
    # 4. 技能与槽位状态 (Skill & Slots State)
    # ---------------------------------------------------------
    skill_id: str = "unknown"
    confidence: float = 0.0
    # 槽位键值对，例如: {"payee": "张三", "amount": 500, "currency": None}
    slots_state: Dict[str, Any] = Field(default_factory=dict)

    # 状态标记 (保持系统健壮性)
    is_rejected: bool = False
    rejection_reason: Optional[str] = None

    # 歧义候选列表
    ambiguous_candidates: Dict[str, Any] = Field(default_factory=dict)

    # 缺失槽位列表
    missing_slots: List[str] = Field(default_factory=list)

    # 动作和响应文本
    action: Optional[str] = None
    response_text: Optional[str] = None

    # 大模型原始返回结果（用于调试）
    llm_raw_response: Optional[Any] = None
    # 发送给大模型的prompt（用于调试）
    prompt: Optional[str] = None
    # 使用的模型名称（用于调试）
    model_name: Optional[str] = None
    
    # LangFuse 追踪 URL（用于可观测性）
    langfuse_trace_url: Optional[str] = None

    # 步骤耗时信息（用于调试和优化）
    step1_duration: Optional[float] = None  # 安全围栏耗时
    step2_duration: Optional[float] = None  # 上下文加载耗时
    step3_duration: Optional[float] = None  # 实体提取耗时
    step4_duration: Optional[float] = None  # 技能识别耗时
    step5_duration: Optional[float] = None  # 任务分发耗时
    step6_duration: Optional[float] = None  # 保存上下文耗时

    # ---------------------------------------------------------
    # 5. 动作建议 (Action Directive - 给Agent编排层的最终指令)
    # ---------------------------------------------------------
    # 格式规范设计，例如:
    # {
    #   "response_type": "CLARIFY" | "EXECUTION" | "FALLBACK",
    #   ... 其他字段
    # }
    action_suggestion: Optional[Dict[str, Any]] = None
    # 示例: {"response_type": "CLARIFY", "clarify_reason": "MISSING_SLOTS", ...}
    # 动作建议列表，支持多个意图的队列执行
    action_suggestions: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    # 示例: [{"action": "EXECUTE", "skill": "SKILL_DEPOSIT_QUERY_V1", ...}, ...]

    model_config = {
        "arbitrary_types_allowed": True
    }
