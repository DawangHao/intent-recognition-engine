"""
实体提取器模块 (step3_extractor.py)

模块功能：
- 从用户输入中提取企业实体信息
- 支持从CSV文件加载企业数据（企业信息.csv 或 bank_customers.csv）
- 处理企业名称歧义，提供候选列表
- 支持提取多个企业实体，避免重叠匹配

核心类：
- Extractor: 提取器基类，定义提取接口
- CustomerExtractor: 企业客户提取器，负责提取企业实体
- ExtractionRegistry: 提取器注册表，管理多个提取器

核心方法：
- extract_entities: 执行实体提取的主函数
  - 参数: context (IntentContext) - 意图上下文对象
  - 返回: IntentContext - 更新后的意图上下文，包含提取的实体信息

配置依赖：
- config.DATA_DIR: 数据目录路径
- config.CUSTOMERS_PATH: 客户数据文件路径

使用示例：
```python
from intent_engine.step3_extractor import extract_entities
from backend.schemas import IntentContext

# 创建上下文对象
context = IntentContext(
    user_id="test_user",
    app_id="Lingxi",
    session_id="test_session",
    raw_query="给我比亚迪和通用电气的访前一页纸"
)

# 执行实体提取
result = extract_entities(context)
print(f"原始查询: {result.raw_query}")
print(f"标准化查询: {result.normalized_query}")
print(f"提取的企业: {result.slots_state.get('target_companies', [])}")
print(f"歧义候选: {result.ambiguous_candidates}")
```

输出示例：
```
原始查询: 给我比亚迪和通用电气的访前一页纸
标准化查询: 给我<AMBIGUOUS_ENTITY key="比亚迪"/>和<AMBIGUOUS_ENTITY key="通用电气"/>的访前一页纸
(1) 无锡比亚迪科技有限公司
(2) 常州比亚迪电池技术有限公司
(3) 南京比亚迪半导体研究所
(1) 南京通用电气有限公司
(2) 南京通用电气集团
(3) 杭州通用电气设备有限公司
(4) 宁波通用电气科技研发有限公司
提取的企业: []
歧义候选: {'比亚迪': [...], '通用电气': [...]}
```

设计特点：
- 使用FlashText库进行高效的关键词匹配
- 支持企业名称和简称的映射
- 处理实体重叠，优先匹配更长的关键词
- 去重企业列表，避免重复候选
- 支持多个企业实体的提取
- 容错处理，数据加载失败时抛出异常
"""
import csv
import os
from typing import Dict, List, Any
from flashtext import KeywordProcessor

from backend.schemas import IntentContext
from backend.config import config
from backend.core.exceptions import ExtractorError

class Extractor:
    """提取器基类"""
    def extract(self, context: IntentContext) -> IntentContext:
        """提取实体
        
        Args:
            context (IntentContext): 意图上下文对象
            
        Returns:
            IntentContext: 更新后的意图上下文
        """
        raise NotImplementedError


class CustomerExtractor(Extractor):
    """企业客户提取器，负责从用户输入中提取企业实体"""
    def __init__(self):
        """初始化企业客户提取器
        
        - 加载企业客户数据
        - 构建关键词处理器
        """
        self.keyword_processor = KeywordProcessor()
        self.alias_map = self._load_customers()
        self._build_keyword_processor()
    
    def _load_customers(self) -> Dict[str, List[Dict[str, str]]]:
        """加载企业客户数据（支持 企业信息.csv 格式）
        
        Returns:
            Dict[str, List[Dict[str, str]]]: 企业别名到企业列表的映射
            
        Raises:
            ExtractorError: 加载客户数据失败时抛出
        """
        alias_map = {}
        try:
            # 优先使用 企业信息.csv
            company_csv_path = os.path.join(config.DATA_DIR, '企业信息.csv')
            
            if os.path.exists(company_csv_path):
                # 使用 企业信息.csv 格式
                with open(company_csv_path, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        company_name = row.get('企业名称', '')
                        company_alias = row.get('企业简称', '')
                        company_id = row.get('企业ID', '')
                        
                        if company_name:
                            # 建立企业名称到企业的映射
                            if company_name not in alias_map:
                                alias_map[company_name] = []
                            alias_map[company_name].append({
                                'id': company_id,
                                'name': company_name
                            })
                        
                        if company_alias:
                            # 建立企业简称到企业的映射
                            if company_alias not in alias_map:
                                alias_map[company_alias] = []
                            alias_map[company_alias].append({
                                'id': company_id,
                                'name': company_name
                            })
            else:
                # 回退到 bank_customers.csv 格式
                with open(config.CUSTOMERS_PATH, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        full_name = row.get('customer_full_name', '')
                        short_name = row.get('customer_short_name', '')
                        customer_id = row.get('customer_id', '')
                        
                        # 建立简称到企业的映射
                        if short_name and short_name not in alias_map:
                            alias_map[short_name] = []
                        if short_name:
                            alias_map[short_name].append({
                                'id': customer_id,
                                'name': full_name
                            })
                        
                        # 建立全称为企业的映射
                        if full_name and full_name not in alias_map:
                            alias_map[full_name] = []
                        if full_name:
                            alias_map[full_name].append({
                                'id': customer_id,
                                'name': full_name
                            })
        except Exception as e:
            raise ExtractorError(f"加载客户数据失败: {e}")
        return alias_map
    
    def _build_keyword_processor(self):
        """构建 FlashText 关键词处理器"""
        for alias in self.alias_map:
            self.keyword_processor.add_keyword(alias, alias)
    
    def extract(self, context: IntentContext) -> IntentContext:
        """提取企业实体
        
        Args:
            context (IntentContext): 意图上下文对象
            
        Returns:
            IntentContext: 更新后的意图上下文，包含提取的实体信息
        """
        if not context.raw_query:
            context.normalized_query = context.raw_query
            return context
        
        # 初始化 normalized_query
        normalized_query = context.raw_query
        
        # 查找所有匹配的关键词
        matches = self.keyword_processor.extract_keywords(context.raw_query, span_info=True)
        
        # 按匹配长度降序排序（优先匹配更长的关键词）
        matches.sort(key=lambda x: x[2] - x[1], reverse=True)
        
        # 处理匹配结果，避免重叠
        processed_ranges = []
        ambiguous_candidates = {}
        target_companies = []
        
        for match in matches:
            alias, start, end = match
            
            # 检查是否与已处理的范围重叠
            overlap = False
            for processed_start, processed_end in processed_ranges:
                if not (end <= processed_start or start >= processed_end):
                    overlap = True
                    break
            
            if overlap:
                continue
            
            # 标记为已处理
            processed_ranges.append((start, end))
            
            # 获取匹配的企业列表
            companies = self.alias_map.get(alias, [])
            
            # 去重企业列表（根据企业名称）
            unique_companies = []
            seen_names = set()
            for company in companies:
                if company['name'] not in seen_names:
                    seen_names.add(company['name'])
                    unique_companies.append(company)
            
            if len(unique_companies) == 1:
                # 唯一匹配
                company = unique_companies[0]
                replacement = company['name']
                normalized_query = normalized_query[:start] + replacement + normalized_query[end:]
                
                # 更新槽位
                target_companies.append(company['name'])
                # 存储第一个企业作为主要目标企业
                if not context.slots_state.get('target_company'):
                    context.slots_state['target_company'] = company['name']
                    context.slots_state['customer_id'] = company['id']
            else:
                # 存在歧义
                replacement = f"<AMBIGUOUS_ENTITY key=\"{alias}\"/>"
                normalized_query = normalized_query[:start] + replacement + normalized_query[end:]
                
                # 添加候选企业列表
                candidates_list = []
                for i, company in enumerate(unique_companies, 1):
                    candidates_list.append(f"({i}) {company['name']}")
                if candidates_list:
                    normalized_query += "\n" + "\n".join(candidates_list)
                
                # 存储候选列表
                ambiguous_candidates[alias] = unique_companies
        
        # 存储所有目标企业
        if target_companies:
            context.slots_state['target_companies'] = target_companies
        
        # 存储歧义候选
        if ambiguous_candidates:
            if not hasattr(context, 'ambiguous_candidates'):
                context.ambiguous_candidates = {}
            context.ambiguous_candidates.update(ambiguous_candidates)
        
        context.normalized_query = normalized_query
        return context


class ExtractionRegistry:
    """提取器注册表，管理多个提取器"""
    def __init__(self):
        """初始化提取器注册表"""
        self.extractors = []
    
    def register(self, extractor: Extractor):
        """注册提取器
        
        Args:
            extractor (Extractor): 提取器实例
        """
        self.extractors.append(extractor)
    
    def process(self, context: IntentContext) -> IntentContext:
        """依次执行所有提取器
        
        Args:
            context (IntentContext): 意图上下文对象
            
        Returns:
            IntentContext: 更新后的意图上下文
        """
        for extractor in self.extractors:
            context = extractor.extract(context)
        return context


# 初始化提取器注册表
registry = ExtractionRegistry()
registry.register(CustomerExtractor())


# 导出处理函数
def extract_entities(context: IntentContext) -> IntentContext:
    """执行实体提取
    
    Args:
        context (IntentContext): 意图上下文对象
        
    Returns:
        IntentContext: 更新后的意图上下文，包含提取的实体信息
    """
    return registry.process(context)
