"""
自定义异常类模块 (exceptions.py)

模块功能：
- 定义意图引擎的自定义异常类
- 建立异常层次结构，便于错误分类和处理
- 提供清晰的错误类型，便于定位和调试

异常层次结构：
- Exception
  └── IntentEngineError (意图引擎基础异常)
      ├── ConfigError (配置错误)
      ├── RedisError (Redis操作错误)
      ├── LLMError (大模型调用错误)
      ├── ExtractorError (实体提取错误)
      └── SlotError (槽位处理错误)

异常说明：

1. IntentEngineError - 意图引擎基础异常
   - 所有意图引擎相关异常的基类
   - 用于捕获所有意图引擎相关的错误

2. ConfigError - 配置错误
   - 当配置文件加载失败或配置参数无效时抛出
   - 例如：缺少必要的配置项、配置值格式错误等

3. RedisError - Redis操作错误
   - 当Redis连接或操作失败时抛出
   - 例如：Redis连接超时、Redis命令执行失败等

4. LLMError - 大模型调用错误
   - 当大模型API调用失败时抛出
   - 例如：API密钥无效、网络连接超时、模型返回格式错误等

5. ExtractorError - 实体提取错误
   - 当实体提取过程中出现错误时抛出
   - 例如：客户数据文件加载失败、提取算法错误等

6. SlotError - 槽位处理错误
   - 当槽位处理过程中出现错误时抛出
   - 例如：槽位验证失败、槽位填充错误等

使用示例：

```python
from backend.core.exceptions import (
    IntentEngineError, ConfigError, RedisError,
    LLMError, ExtractorError, SlotError
)

# 捕获特定异常
try:
    # 执行可能抛出异常的代码
    pass
except ConfigError as e:
    print(f"配置错误: {e}")
except RedisError as e:
    print(f"Redis错误: {e}")
except LLMError as e:
    print(f"大模型错误: {e}")
except ExtractorError as e:
    print(f"实体提取错误: {e}")
except SlotError as e:
    print(f"槽位处理错误: {e}")
except IntentEngineError as e:
    print(f"意图引擎错误: {e}")
except Exception as e:
    print(f"其他错误: {e}")

# 抛出异常
def load_config():
    if not os.getenv("VOLCENGINE_API_KEY"):
        raise ConfigError("缺少火山引擎API密钥")
```

设计特点：
- 清晰的异常层次结构，便于错误分类和处理
- 统一的异常基类，便于捕获所有意图引擎相关错误
- 具体的异常类型，便于精确定位错误原因
- 简单的异常定义，便于扩展和维护
"""
# 自定义异常类

class IntentEngineError(Exception):
    """意图引擎基础异常"""
    pass


class ConfigError(IntentEngineError):
    """配置错误"""
    pass


class RedisError(IntentEngineError):
    """Redis操作错误"""
    pass


class LLMError(IntentEngineError):
    """大模型调用错误"""
    pass


class ExtractorError(IntentEngineError):
    """实体提取错误"""
    pass


class SlotError(IntentEngineError):
    """槽位处理错误"""
    pass
