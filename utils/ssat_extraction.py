"""
SSAT (Semantic Software Architecture Tree) 提取器
参考论文：Towards Realistic Project-Level Code Generation via Multi-Agent Collaboration
提取代码的语义架构信息，用于重构分析
"""
import ast
import json
import os
from pathlib import Path
from typing import Dict, List, Any


class SSATExtractorAST:
    """用ast模块提取代码的SSAT结构，包含丰富的语义信息"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.ssat = {
            "file_name": os.path.basename(file_path),
            "classes": {},
            "functions": [],  # 模块级函数
            "imports": []  # 导入信息
        }

    def extract(self) -> Dict:
        """
        提取完整的SSAT结构
        
        Returns:
            包含类、方法、函数、导入等信息的字典
        """
        with open(self.file_path, "r", encoding="utf-8") as f:
            code = f.read()
        
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise ValueError(f"代码语法错误: {e}")
        
        # 提取导入信息
        self._extract_imports(tree)
        
        # 提取模块级函数
        self._extract_module_functions(tree)
        
        # 提取类信息
        self._extract_classes(tree)
        
        return self.ssat
    
    def _extract_imports(self, tree: ast.AST):
        """提取导入信息"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.ssat["imports"].append({
                        "type": "import",
                        "module": alias.name,
                        "alias": alias.asname
                    })
            elif isinstance(node, ast.ImportFrom):
                self.ssat["imports"].append({
                    "type": "from_import",
                    "module": node.module or "",
                    "names": [alias.name for alias in node.names]
                })
    
    def _extract_module_functions(self, tree: ast.AST):
        """提取模块级函数"""
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = self._extract_function_info(node)
                self.ssat["functions"].append(func_info)
    
    def _extract_classes(self, tree: ast.AST):
        """提取类信息"""
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                class_info = self._extract_class_info(node)
                self.ssat["classes"][node.name] = class_info
    
    def _extract_class_info(self, class_node: ast.ClassDef) -> Dict[str, Any]:
        """提取类的详细信息"""
        methods = []
        class_variables = []
        
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._extract_function_info(item)
                methods.append(method_info)
            elif isinstance(item, ast.Assign):
                # 类变量
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        class_variables.append({
                            "name": target.id,
                            "type": "class_variable"
                        })
        
        return {
            "methods": methods,
            "class_variables": class_variables,
            "bases": [self._get_name(base) for base in class_node.bases],
            "docstring": ast.get_docstring(class_node)
        }
    
    def _extract_function_info(self, func_node: ast.FunctionDef) -> Dict[str, Any]:
        """提取函数的详细信息"""
        # 提取参数
        params = []
        for param in func_node.args.args:
            param_info = {
                "name": param.arg,
                "annotation": self._get_annotation(param.annotation) if param.annotation else None
            }
            params.append(param_info)
        
        # 计算复杂度指标
        complexity = self._calculate_complexity(func_node)
        
        return {
            "name": func_node.name,
            "parameters": [p["name"] for p in params],  # 保持向后兼容
            "parameters_detail": params,
            "return_annotation": self._get_annotation(func_node.returns) if func_node.returns else None,
            "docstring": ast.get_docstring(func_node),
            "complexity": complexity,
            "line_count": func_node.end_lineno - func_node.lineno + 1 if hasattr(func_node, 'end_lineno') else None
        }
    
    def _calculate_complexity(self, func_node: ast.FunctionDef) -> Dict[str, Any]:
        """计算函数复杂度指标"""
        complexity_metrics = {
            "cyclomatic_complexity": 1,  # 基础复杂度为1
            "nesting_depth": 0,
            "statement_count": 0
        }
        
        def visit_node(node, depth=0):
            complexity_metrics["nesting_depth"] = max(complexity_metrics["nesting_depth"], depth)
            
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity_metrics["cyclomatic_complexity"] += 1
            
            if isinstance(node, ast.stmt):
                complexity_metrics["statement_count"] += 1
            
            for child in ast.iter_child_nodes(node):
                visit_node(child, depth + 1 if isinstance(node, (ast.If, ast.While, ast.For, ast.Try, ast.With)) else depth)
        
        visit_node(func_node)
        
        return complexity_metrics
    
    def _get_annotation(self, node: ast.AST) -> str:
        """获取类型注解的字符串表示"""
        if node is None:
            return None
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return str(node.value)
        else:
            return ast.unparse(node) if hasattr(ast, 'unparse') else str(node)
    
    def _get_name(self, node: ast.AST) -> str:
        """获取节点名称"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        else:
            return str(node)