"""
重构引擎 - 整合重构机会识别和补丁生成
"""
import json
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

from utils.ssat_extraction import SSATExtractorAST
from utils.llm_client import LLMClient


class RefactorEngine:
    """重构引擎 - 整合机会识别和补丁生成"""
    
    def __init__(self, llm_client: LLMClient = None):
        self.llm_client = llm_client or LLMClient()
    
    def detect_opportunities(self, code_path: str) -> List[Dict[str, Any]]:
        """识别重构机会"""
        # 提取SSAT
        extractor = SSATExtractorAST(code_path)
        ssat = extractor.extract()
        
        # 读取代码
        with open(code_path, "r", encoding="utf-8") as f:
            code = f.read()
        
        # 构建提示词
        prompt = self._build_analysis_prompt(code, ssat)
        
        # 调用大模型
        response = self.llm_client.call(
            prompt=prompt,
            system_prompt="你是代码重构专家，擅长识别代码中的设计问题和重构机会。",
            max_tokens=4096,
            temperature=0.2
        )
        
        return self._parse_opportunities(response)
    
    def generate_patch(
        self, 
        original_code: str, 
        opportunities: List[Dict[str, Any]]
    ) -> str:
        """生成重构补丁"""
        prompt = self._build_generation_prompt(original_code, opportunities)
        
        response = self.llm_client.call(
            prompt=prompt,
            system_prompt="你是代码重构专家，擅长生成高质量的重构代码。要求：保持功能一致、遵循最佳实践、代码清晰可读。",
            max_tokens=8192,
            temperature=0.1
        )
        
        return self._extract_code(response)
    
    def _build_analysis_prompt(self, code: str, ssat: Dict) -> str:
        """构建分析提示词"""
        constraints = {
            "单一职责原则": "一个类只负责一项核心功能",
            "DRY原则": "不要重复自己，相同逻辑应封装复用",
            "函数简洁性": "函数应该短小、只做一件事",
            "代码可读性": "代码应该清晰易懂，命名有意义"
        }
        
        return f"""分析以下Python代码，识别重构机会。

## 原始代码
```python
{code}
```

## 代码架构 (SSAT)
```json
{json.dumps(ssat, indent=2, ensure_ascii=False)}
```

## 设计原则
```json
{json.dumps(constraints, indent=2, ensure_ascii=False)}
```

## 输出要求
以JSON格式输出重构机会列表：
```json
[
  {{
    "problem_type": "问题类型",
    "location": "问题位置",
    "description": "详细描述",
    "suggestion": "重构建议",
    "severity": "严重程度(high/medium/low)"
  }}
]
```

直接输出JSON，不要其他文字。"""
    
    def _build_generation_prompt(self, code: str, opportunities: List[Dict]) -> str:
        """构建生成提示词"""
        sorted_opps = sorted(opportunities, key=lambda x: {
            "high": 3, "medium": 2, "low": 1
        }.get(x.get("severity", "medium"), 2), reverse=True)
        
        return f"""根据以下代码和重构机会，生成完整的重构后代码。

## 原始代码
```python
{code}
```

## 重构机会
```json
{json.dumps(sorted_opps, indent=2, ensure_ascii=False)}
```

## 要求
1. 保持功能完全一致
2. 解决所有识别的问题
3. 遵循SOLID原则和最佳实践
4. 代码清晰、可读、可维护
5. 确保代码可直接运行

输出完整Python代码（在```python代码块中）。"""
    
    def _parse_opportunities(self, response: str) -> List[Dict[str, Any]]:
        """解析重构机会"""
        json_match = re.search(r'```json\s*(\[.*?\])\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_match = re.search(r'(\[.*\])', response, re.DOTALL)
            json_str = json_match.group(1) if json_match else response.strip()
        
        try:
            opps = json.loads(json_str)
            if not isinstance(opps, list):
                opps = [opps]
            return [{
                "problem_type": o.get("problem_type", "未知"),
                "location": o.get("location", "未知"),
                "description": o.get("description", ""),
                "suggestion": o.get("suggestion", ""),
                "severity": o.get("severity", "medium")
            } for o in opps if isinstance(o, dict)]
        except json.JSONDecodeError:
            return [{
                "problem_type": "解析错误",
                "location": "系统",
                "description": f"无法解析响应: {response[:200]}",
                "suggestion": "请检查API返回",
                "severity": "high"
            }]
    
    def _extract_code(self, response: str) -> str:
        """提取代码"""
        match = re.search(r'```python\s*(.*?)\s*```', response, re.DOTALL)
        if match:
            return match.group(1).strip()
        if response.strip().startswith(('class ', 'def ', 'import ', 'from ')):
            return response.strip()
        return response.strip()

