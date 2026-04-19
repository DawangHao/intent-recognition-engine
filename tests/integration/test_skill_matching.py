import pytest
import json
import os

class TestSkillMatching:
    def test_skill_list_matching(self):
        """测试灵犀技能清单是否与JSON文件匹配"""
        # 读取灵犀前端的技能表（从HTML文件中提取）
        frontend_skills = {
            "SKILL_DEPOSIT_QUERY_V1": {
                "name": "查询存款",
                "apiEndpoint": "/api/deposit/query",
                "uiComponent": "DEPOSIT_CARD"
            },
            "SKILL_LOAN_QUERY_V1": {
                "name": "查询贷款",
                "apiEndpoint": "/api/loan/query",
                "uiComponent": "LOAN_CARD"
            },
            "SKILL_VISIT_REPORT_V1": {
                "name": "获取访前一页纸",
                "apiEndpoint": "/api/visit-report/download",
                "uiComponent": "VISIT_REPORT"
            }
        }
        
        # 读取意图引擎的技能配置文件
        intent_engine_skills = {}
        skill_files = ["FQYYZ.json", "CXDK.json", "CXCK.json"]
        for file_name in skill_files:
            file_path = os.path.join("intent_engine", file_name)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    skill_data = json.load(f)
                    intent_engine_skills[skill_data["skill_id"]] = skill_data
        
        # 检查技能ID是否匹配
        for skill_id in frontend_skills:
            assert skill_id in intent_engine_skills
        
        # 检查技能参数是否对应
        for skill_id, frontend_skill in frontend_skills.items():
            intent_skill = intent_engine_skills[skill_id]
            assert "slots" in intent_skill
            # 检查必要参数
            required_slots = [slot for slot in intent_skill["slots"] if slot.get("is_required", False)]
            assert len(required_slots) > 0