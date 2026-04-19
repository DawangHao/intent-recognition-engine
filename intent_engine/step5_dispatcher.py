"""
任务分发模块 (step5_dispatcher.py)

模块功能：
- 处理大模型返回的意图识别结果
- 构建动作建议列表，支持多意图队列
- 生成响应文本，用于上下文记录
- 支持向后兼容，处理不同格式的返回结果

核心类：
- Dispatcher: 任务分发器，负责处理意图识别结果并构建响应

核心方法：
- dispatch: 处理意图识别结果并构建响应
  - 参数: context (IntentContext) - 意图上下文对象
  - 返回: IntentContext - 更新后的意图上下文，包含动作建议和响应文本

使用示例：
```python
from intent_engine.step5_dispatcher import dispatcher
from backend.schemas import IntentContext

# 创建上下文对象
context = IntentContext(
    user_id="test_user",
    app_id="Lingxi",
    session_id="test_session",
    raw_query="给我比亚迪的存款和贷款信息"
)

# 设置大模型返回结果
context.llm_raw_response = [
    {
        "intent": "查询企业的本外币合计对公存款余额",
        "confidence": 0.95,
        "action": "EXECUTE",
        "skill": "SKILL_DEPOSIT_QUERY_V1",
        "parameters": {"target_company": "比亚迪"}
    },
    {
        "intent": "查询企业的本外币合计总贷款余额",
        "confidence": 0.90,
        "action": "EXECUTE",
        "skill": "SKILL_LOAN_QUERY_V1",
        "parameters": {"target_company": "比亚迪"}
    }
]

# 执行任务分发
result = dispatcher.dispatch(context)
print(f"响应文本: {result.response_text}")
print(f"动作建议: {result.action_suggestions}")
```

输出示例：
```
响应文本: 查询比亚迪的存款
动作建议: [{'action': 'EXECUTE', 'skill': 'SKILL_DEPOSIT_QUERY_V1', 'parameters': {'target_company': '比亚迪'}, 'response_text': ''}, {'action': 'EXECUTE', 'skill': 'SKILL_LOAN_QUERY_V1', 'parameters': {'target_company': '比亚迪'}, 'response_text': ''}]
```

设计特点：
- 支持多意图队列，处理多个技能的顺序执行
- 向后兼容，支持单个意图对象和数组格式
- 自动生成响应文本，丰富上下文记录
- 支持EXECUTE、CLARIFY、FALLBACK三种动作类型
- 容错处理，确保即使返回格式异常也能正常处理
"""
import json
from typing import Dict, Any

from backend.schemas import IntentContext

class Dispatcher:
    """任务分发器，负责处理意图识别结果并构建响应"""
    def __init__(self):
        """初始化任务分发器"""
        pass
    
    def dispatch(self, context: IntentContext) -> IntentContext:
        """处理意图识别结果并构建响应
        
        Args:
            context (IntentContext): 意图上下文对象
            
        Returns:
            IntentContext: 更新后的意图上下文，包含动作建议和响应文本
        """
        # 获取大模型原始返回结果
        llm_raw_response = getattr(context, 'llm_raw_response', {})
        if llm_raw_response is None:
            llm_raw_response = {}
        
        # 检查是否已经在intent_core中处理了action_suggestions
        if hasattr(context, 'action_suggestions') and context.action_suggestions:
            print("[DISPATCHER] Using existing action_suggestions list")
            # 确保action_suggestion也被设置（向后兼容）
            if context.action_suggestions:
                # 生成响应文本
                first_action = context.action_suggestions[0] if isinstance(context.action_suggestions, list) else context.action_suggestion
                if first_action.get('action') == 'EXECUTE':
                    skill = first_action.get('skill', '')
                    parameters = first_action.get('parameters', {})
                    company_name = parameters.get('company_name', parameters.get('target_company', ''))
                    if skill == 'SKILL_DEPOSIT_QUERY_V1' and company_name:
                        context.response_text = f"查询{company_name}的存款"
                    elif skill == 'SKILL_LOAN_QUERY_V1' and company_name:
                        context.response_text = f"查询{company_name}的贷款"
                    elif skill == 'SKILL_VISIT_REPORT_V1' and company_name:
                        context.response_text = f"获取{company_name}的访前一页纸"
                    elif skill == 'SKILL_SETTLEMENT_QUERY_V1' and company_name:
                        context.response_text = f"查询{company_name}的结算分"
                    else:
                        context.response_text = f"执行{skill}操作"
                elif first_action.get('action') == 'CLARIFY':
                    context.response_text = first_action.get('response_text', '')
                else:  # FALLBACK
                    context.response_text = first_action.get('response_text', '我不太理解您的问题，请换个方式表述')
            return context
        
        # 如果没有现成的action_suggestions，从llm_raw_response处理
        # 检查是否是数组格式
        if isinstance(llm_raw_response, list) and len(llm_raw_response) > 0:
            print("[DISPATCHER] Processing llm_raw_response as array")
            action_suggestions = []
            
            # 构建动作建议列表
            for intent in llm_raw_response:
                action_suggestion = {
                    "action": intent.get('action', 'EXECUTE'),
                    "skill": intent.get('skill', ''),
                    "parameters": intent.get('parameters', {}),
                    "response_text": intent.get('response_text', '')
                }
                action_suggestions.append(action_suggestion)
            
            # 更新动作建议列表
            context.action_suggestions = action_suggestions
            
            # 设置第一个动作建议作为单独的action_suggestion
            context.action_suggestion = action_suggestions[0] if action_suggestions else None
            
            # 生成响应文本
            first_action = context.action_suggestion
            if first_action:
                if first_action.get('action') == 'EXECUTE':
                    skill = first_action.get('skill', '')
                    parameters = first_action.get('parameters', {})
                    company_name = parameters.get('company_name', parameters.get('target_company', ''))
                    if skill == 'SKILL_DEPOSIT_QUERY_V1' and company_name:
                        context.response_text = f"查询{company_name}的存款"
                    elif skill == 'SKILL_LOAN_QUERY_V1' and company_name:
                        context.response_text = f"查询{company_name}的贷款"
                    elif skill == 'SKILL_VISIT_REPORT_V1' and company_name:
                        context.response_text = f"获取{company_name}的访前一页纸"
                    elif skill == 'SKILL_SETTLEMENT_QUERY_V1' and company_name:
                        context.response_text = f"查询{company_name}的结算分"
                    else:
                        context.response_text = f"执行{skill}操作"
                elif first_action.get('action') == 'CLARIFY':
                    context.response_text = first_action.get('response_text', '')
                else:  # FALLBACK
                    context.response_text = first_action.get('response_text', '我不太理解您的问题，请换个方式表述')
            
            return context
        
        # 单个对象的情况（向后兼容）
        print("[DISPATCHER] Processing single intent object")
        # 获取action类型
        action = llm_raw_response.get('action', 'FALLBACK')
        
        # 根据action类型构建不同的响应格式
        if action == 'EXECUTE':
            # 构建EXECUTE响应
            skill = llm_raw_response.get('skill', '')
            parameters = llm_raw_response.get('parameters', {})
            context.action_suggestion = {
                "action": "EXECUTE",
                "skill": skill,
                "parameters": parameters
            }
            context.action_suggestions = [context.action_suggestion]
            # 生成更具体的响应文本，用于上下文记录
            company_name = parameters.get('company_name', parameters.get('target_company', ''))
            if skill == 'SKILL_DEPOSIT_QUERY_V1' and company_name:
                context.response_text = f"查询{company_name}的存款"
            elif skill == 'SKILL_LOAN_QUERY_V1' and company_name:
                context.response_text = f"查询{company_name}的贷款"
            elif skill == 'SKILL_VISIT_REPORT_V1' and company_name:
                context.response_text = f"获取{company_name}的访前一页纸"
            elif skill == 'SKILL_SETTLEMENT_QUERY_V1' and company_name:
                context.response_text = f"查询{company_name}的结算分"
            else:
                context.response_text = f"执行{skill}操作"

        elif action == 'CLARIFY':
            # 构建CLARIFY响应
            response_text = llm_raw_response.get('response_text', '')
            context.action_suggestion = {
                "action": "CLARIFY",
                "response_text": response_text
            }
            context.action_suggestions = [context.action_suggestion]
            # 保存响应文本到context
            context.response_text = response_text
        else:  # FALLBACK
            # 构建FALLBACK响应
            response_text = llm_raw_response.get('response_text', '我不太理解您的问题，请换个方式表述')
            context.action_suggestion = {
                "action": "FALLBACK",
                "response_text": response_text
            }
            context.action_suggestions = [context.action_suggestion]
            # 保存响应文本到context
            context.response_text = response_text
        
        return context


# 导出实例
dispatcher = Dispatcher()
