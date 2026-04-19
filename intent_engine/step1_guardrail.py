"""
安全围栏模块 (step1_guardrail.py)

模块功能：
- 对用户输入进行安全检查，过滤包含敏感词的查询
- 加载并使用预定义的黑名单关键词列表
- 标记被拒绝的查询并提供拒绝原因

核心类：
- Guardrail: 安全围栏主类，负责检查用户输入是否包含敏感词

核心方法：
- check: 检查用户输入是否包含黑名单关键词
  - 参数: context (IntentContext) - 意图上下文对象
  - 返回: IntentContext - 更新后的意图上下文，包含拒绝状态和原因

配置依赖：
- config.BLACKLIST_PATH: 黑名单文件路径

使用示例：
```python
from intent_engine.step1_guardrail import guardrail
from backend.schemas import IntentContext

# 创建上下文对象
context = IntentContext(
    user_id="test_user",
    app_id="Lingxi",
    session_id="test_session",
    raw_query="查询赌博相关信息"
)

# 执行安全检查
result = guardrail.check(context)
print(f"是否被拒绝: {result.is_rejected}")
print(f"拒绝原因: {result.rejection_reason}")
```

输出示例：
```
是否被拒绝: True
拒绝原因: 包含敏感词: 赌博
```
"""
import re

from backend.schemas import IntentContext
from backend.config import config

class Guardrail:
    """安全围栏类，负责检查用户输入是否包含敏感词"""
    def __init__(self):
        """初始化安全围栏，加载黑名单"""
        self.blacklist = self._load_blacklist()
    
    def _load_blacklist(self):
        """加载黑名单关键词
        
        Returns:
            list: 黑名单关键词列表
        """
        try:
            with open(config.BLACKLIST_PATH, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception:
            return []
    
    def check(self, context: IntentContext) -> IntentContext:
        """检查是否包含黑名单关键词
        
        Args:
            context (IntentContext): 意图上下文对象
            
        Returns:
            IntentContext: 更新后的意图上下文，包含拒绝状态和原因
        """
        if not context.raw_query:
            return context
        
        for keyword in self.blacklist:
            if re.search(keyword, context.raw_query):
                context.is_rejected = True
                context.rejection_reason = f"包含敏感词: {keyword}"
                break
        
        return context


# 导出实例
guardrail = Guardrail()
