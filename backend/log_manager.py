"""
对话日志管理模块 (log_manager.py)

模块功能：
- 完整记录用户与智能体的所有交互历史
- 支持按日期和会话ID分文件存储
- 提供JSON格式的结构化日志
- 支持日志查询和检索功能

核心类：
- InteractionLogger: 交互日志管理类，负责记录和查询对话历史

使用示例：
```python
from backend.log_manager import interaction_logger
from backend.schemas import IntentContext

# 记录一次完整交互
interaction_logger.log_interaction(
    user_id="test_user",
    app_id="Lingxi",
    session_id="test_session",
    context=intent_context,
    result=result_context
)
```
"""
import os
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from backend.config import config
from backend.schemas import IntentContext


class InteractionLogger:
    """交互日志管理类，负责记录和查询对话历史"""
    
    def __init__(self):
        """初始化日志管理器"""
        # 日志目录
        self.logs_dir = os.path.join(config.ROOT_DIR, "logs")
        # 确保日志目录存在
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # 对话记录目录
        self.conversation_dir = os.path.join(self.logs_dir, "conversations")
        os.makedirs(self.conversation_dir, exist_ok=True)
        
        print(f"[LOGGER] 日志目录: {self.logs_dir}")
    
    def _get_session_log_path(self, user_id: str, app_id: str, session_id: str) -> str:
        """获取会话日志文件路径
        
        Args:
            user_id (str): 用户ID
            app_id (str): 应用ID
            session_id (str): 会话ID
            
        Returns:
            str: 日志文件路径
        """
        # 按日期组织目录
        today = datetime.now().strftime("%Y-%m-%d")
        date_dir = os.path.join(self.conversation_dir, today)
        os.makedirs(date_dir, exist_ok=True)
        
        # 文件名格式: app_id_user_id_session_id.json
        filename = f"{app_id.lower()}_{user_id}_{session_id}.json"
        return os.path.join(date_dir, filename)
    
    def log_interaction(
        self,
        user_id: str,
        app_id: str,
        session_id: str,
        context: IntentContext,
        result: Any = None
    ):
        """记录一次完整的用户交互
        
        Args:
            user_id (str): 用户ID
            app_id (str): 应用ID
            session_id (str): 会话ID
            context (IntentContext): 输入上下文
            result (Any): 处理结果
        """
        try:
            log_path = self._get_session_log_path(user_id, app_id, session_id)
            
            # 加载现有日志（如果存在）
            conversation_log = []
            if os.path.exists(log_path):
                with open(log_path, 'r', encoding='utf-8') as f:
                    conversation_log = json.load(f)
            
            # 构建本次交互的日志记录
            interaction = {
                "timestamp": time.time(),
                "timestamp_str": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "user_input": context.raw_query,
                "normalized_query": getattr(context, 'normalized_query', context.raw_query),
                "final_query": getattr(context, 'final_query', context.raw_query),
                "skill_id": getattr(context, 'skill_id', ''),
                "confidence": getattr(context, 'confidence', 0.0),
                "action": getattr(context, 'action', ''),
                "response_text": getattr(context, 'response_text', ''),
                "slots_state": getattr(context, 'slots_state', {}),
                "ambiguous_candidates": getattr(context, 'ambiguous_candidates', {}),
                "missing_slots": getattr(context, 'missing_slots', []),
                "step_durations": {
                    "step1_guardrail": getattr(context, 'step1_duration', 0.0),
                    "step2_context": getattr(context, 'step2_duration', 0.0),
                    "step3_extractor": getattr(context, 'step3_duration', 0.0),
                    "step4_intent_core": getattr(context, 'step4_duration', 0.0),
                    "step5_dispatcher": getattr(context, 'step5_duration', 0.0),
                    "step6_api": getattr(context, 'step6_duration', 0.0)
                }
            }
            
            # 如果有结果，添加结果信息
            if result:
                # 从结果中提取信息
                interaction["result"] = {
                    "skill_id": getattr(result, 'skill_id', ''),
                    "confidence": getattr(result, 'confidence', 0.0),
                    "action": getattr(result, 'action', ''),
                    "response_text": getattr(result, 'response_text', ''),
                    "slots_state": getattr(result, 'slots_state', {})
                }
            
            # 添加到对话记录
            conversation_log.append(interaction)
            
            # 保存到文件
            with open(log_path, 'w', encoding='utf-8') as f:
                json.dump(conversation_log, f, ensure_ascii=False, indent=2)
            
            print(f"[LOGGER] 已记录交互: {log_path}")
            
        except Exception as e:
            print(f"[LOGGER] 记录日志失败: {e}")
    
    def get_conversation_history(
        self,
        user_id: str,
        app_id: str,
        session_id: str,
        date: Optional[str] = None
    ) -> List[Dict]:
        """获取指定会话的对话历史
        
        Args:
            user_id (str): 用户ID
            app_id (str): 应用ID
            session_id (str): 会话ID
            date (Optional[str]): 指定日期，格式 YYYY-MM-DD，默认为今天
            
        Returns:
            List[Dict]: 对话历史记录
        """
        try:
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            
            # 构建日志文件路径
            date_dir = os.path.join(self.conversation_dir, date)
            filename = f"{app_id.lower()}_{user_id}_{session_id}.json"
            log_path = os.path.join(date_dir, filename)
            
            if os.path.exists(log_path):
                with open(log_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return []
                
        except Exception as e:
            print(f"[LOGGER] 获取对话历史失败: {e}")
            return []
    
    def get_user_sessions(
        self,
        user_id: str,
        app_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """获取用户最近的会话列表
        
        Args:
            user_id (str): 用户ID
            app_id (str): 应用ID
            limit (int): 返回的会话数量限制
            
        Returns:
            List[Dict]: 会话列表，包含会话ID和最新交互时间
        """
        try:
            sessions = []
            
            # 遍历最近几天的目录
            for i in range(7):  # 最近7天
                date = datetime.now().strftime("%Y-%m-%d")
                # TODO: 这里需要根据实际日期计算
                # 简化实现，直接获取当前日期的所有会话
                date_dir = os.path.join(self.conversation_dir, date)
                if os.path.exists(date_dir):
                    for filename in os.listdir(date_dir):
                        if filename.startswith(f"{app_id.lower()}_{user_id}_"):
                            sessions.append({
                                "date": date,
                                "session_id": filename.split('.')[0]
                            })
            
            return sessions[:limit]
            
        except Exception as e:
            print(f"[LOGGER] 获取用户会话失败: {e}")
            return []


# 导出实例
interaction_logger = InteractionLogger()
